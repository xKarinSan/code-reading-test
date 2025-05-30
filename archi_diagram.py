import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.prompts.chat import ChatPromptTemplate

from files import scan_subfolders, read_contents
from rag_test import read_all_file_contents
from const import paths

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def clean_mermaid_output(output: str) -> str:
    """
    Removes ```mermaid and ``` wrapping if present.
    """
    output = output.strip()
    if output.startswith("```mermaid"):
        output = output[len("```mermaid"):].strip()
    if output.startswith("```"):
        output = output[len("```"):].strip()
    if output.endswith("```"):
        output = output[:-3].strip()
    return output

def generate_diagram_with_rag(vector_store, model,index):
    print("[📚] Retrieving all content from vector DB for summarization...")

    results = vector_store.similarity_search(
        query="What are the main components and their relationships in the codebase?",
        k=50
    )
    key_extensions = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cs",
        ".cpp",
        ".c",
        ".go",
        ".rb",
        ".php",
        ".rs",
        ".kt",
        ".swift",
        ".scala",
        ".sh",
        ".pl",
        ".dart",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
        ".sql",
        ".jsx",
        ".tsx",
    }
    
    filtered_docs = []
    for doc in results:
        metadata = doc.metadata
        ext = metadata.get("extension", "").lower()
        if ext and (ext.startswith(".") and ext in key_extensions) or (f".{ext}" in key_extensions):
            filtered_docs.append(doc.page_content)

    full_context = "\n".join(filtered_docs)

    architecture_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior software architect. Your job is to analyze codebases and generate accurate, high-level architecture diagrams using Mermaid."
            
            "Analyze the structure and purpose of the following. Determine its architectural style or design pattern if applicable (e.g., monolithic, client-server, layered, microservices, modular, or single-purpose).\n\n"
            "Then, generate a **high-level architecture diagram** that shows the main components and how they interact or relate to each other.\n\n"
            "Abstract the system into logical components such as:\n"
            "- Frontend or UI layer (if any)\n"
            "- Backend or API services\n"
            "- Databases or storage\n"
            "- Background jobs, workers, or schedulers\n"
            "- Third-party integrations or cloud services\n"
            "- Configuration or environment dependencies\n"
            "- Core modules or internal layers (e.g., `Compiler`, `CLI`, `SDK`, etc.)\n\n"
            "Use **Mermaid syntax** in `graph TD` layout:\n"
            "- Group related parts into `subgraph` blocks (e.g., `Frontend`, `Backend`, `Database`, `External Services`, `Core Modules`).\n"
            "- Show **connections both within subgraphs and between subgraphs**, if components interact.\n"
            "- Use directional arrows to show communication flow, data flow, or dependency relationships.\n"
            "- Label each node with concise, meaningful names (e.g., `React Frontend`, `Node.js API`, `Redis Cache`, `GitHub API`, `.env Config`, `Parser Module`, `CLI Entry Point`).\n\n"
            "✅ Only output a valid Mermaid diagram inside a code block.\n"
            "🚫 Do not include file paths, filenames, explanations, or extra markdown.\n\n"
            "Example:\n\n"
            "graph TD\n"
            "  subgraph Frontend\n"
            "    A[Next.js App]\n"
            "  end\n"
            "  subgraph Backend\n"
            "    B[Express.js Server]\n"
            "    B --> C[(PostgreSQL)]\n"
            "    B --> D[Stripe API]\n"
            "    B --> E[.env Configuration]\n"
            "  end\n"
            "  A --> B\n\n"
            "Additional guidelines:\n"
            "- If the context includes too much information, focus on the components most essential to the system’s functionality and architecture.\n"
            "- %% Only include high-level logical components, not file names."
            
        ),
        (
            "user",
            "Given the following codebase:\n\n"
            "{context}\n\n"
        )
    ])


    chain = architecture_prompt | model
    readme = chain.invoke({"context": full_context}).content
    readme = clean_mermaid_output(readme)

    with open(f"mermaid_results/testing_mermaid_diagram_{str(index)}.md", "w") as f:
        f.write(readme)

    print("[✅] README.md generated successfully with summarization.")



if __name__ == "__main__":
    print("[🔍] Scanning files...")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Chroma(
        collection_name="codebase_name",
        embedding_function=embeddings,
        persist_directory="./vector_db",
    )


    for idx in range(len(paths)):
        vector_store.reset_collection()

        resultant_files = scan_subfolders(path=paths[idx])
        read_files = read_contents(resultant_files)
        documents, uuids = read_all_file_contents(read_files)
        vector_store.add_documents(documents)
        generate_diagram_with_rag(vector_store, model,idx)
