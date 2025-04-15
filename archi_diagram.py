import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.prompts.chat import ChatPromptTemplate

from files import scan_subfolders, read_contents
from rag_test import read_all_file_contents, summarize_documents


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def generate_diagram_with_rag(vector_store, model):
    print("[📚] Retrieving all content from vector DB for summarization...")
    all_docs = vector_store.get(include=["documents", "metadatas"])
    all_texts = all_docs["documents"]
    all_metas = all_docs["metadatas"]

    # Filter relevant files
    key_extensions = {".py", ".js", ".ts", ".md", ".json", ".html", ".env"}
    filtered_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(all_texts, all_metas)
        if Path(meta["source"]).suffix in key_extensions
    ]

    # Optional: reduce further to top 15 largest files
    summaries = summarize_documents(filtered_docs, model)
    full_context = "\n".join(summaries)
    # print(full_context)

    architecture_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert software engineer who analyzes codebases and generates accurate architecture diagrams in Mermaid format."
        ),
        (
            "user",
            "Given the following codebase context:\n\n"
            "{context}\n\n"
            "Generate a high-level architecture diagram of the codebase using Mermaid syntax.\n\n"
            "Include:\n"
            "- Key components such as frontend, backend, databases, external APIs, or services\n"
            "- Environment-related dependencies (e.g., .env variables, config files)\n"
            "- The interactions and data flow between components\n"
            "- If applicable, represent things like auth flows, job queues, or middleware\n\n"
            "Use `graph TD` (top-down) layout for the diagram. Use meaningful labels (e.g., \"FastAPI Backend\", \"MongoDB\", \"OpenAI API\", etc).\n\n"
            "✅ Only output the diagram as a code block using Mermaid syntax\n"
            "🚫 Do not include any explanation, markdown outside the code block, or introductory text\n\n"
            "Example:\n\n"
            "```mermaid\n"
            "graph TD\n"
            "  A[Frontend - React] --> B[Backend - FastAPI]\n"
            "  B --> C[(MongoDB Database)]\n"
            "  B --> D[External API - OpenAI]\n"
            "  B --> E[.env Variables]\n"
            "```\n"
        )
    ])

    chain = architecture_prompt | model
    readme = chain.invoke({"context": full_context}).content

    with open("testing_mermaid_diagram.md", "w") as f:
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
    vector_store.reset_collection()
    # Change this to your desired repo path
    curr_path = "/Users/demonicaoi/Documents/MERN-Stack"

    resultant_files = scan_subfolders(path=curr_path)
    for file in resultant_files:
        print("file: ", file)

    read_files = read_contents(resultant_files)
    documents, uuids = read_all_file_contents(read_files)
    vector_store.add_documents(documents)
    
    generate_diagram_with_rag(vector_store, model)
