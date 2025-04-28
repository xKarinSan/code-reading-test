import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts.chat import ChatPromptTemplate

from files import scan_subfolders, read_contents
from rag_test import read_all_file_contents


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def generate_readme_with_rag(vector_store, model,idx):
    print("[📚] Retrieving all content from vector DB for summarization...")


    results = vector_store.similarity_search(
        query="What are the main components and their relationships in the codebase?",
        k=50
    )
    
    # Filter relevant files
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

    prompt = ChatPromptTemplate.from_messages([
        ("system",
            """
            You are an expert software engineer who writes clean, production-ready README.md files for codebases.
            
            Your task:
            - Only generate a professional README.md file.
            - Only use clean and valid markdown formatting.
            - Strictly include the following sections, in this order:
            1. **Project Description** – Explain what the project does and its purpose.
            2. **Tech Stack** – List the programming languages, libraries, and frameworks used.
            3. **Environment Variables** – Mention any environment variables required (e.g., API keys, DB configs).
            4. **Setup Instructions** – Include steps to install dependencies and set up the environment.
            5. **Running Instructions** – Provide commands or steps to run the project locally or in production.

            Important Rules:
            - Do NOT generate any Mermaid diagrams.
            - Do NOT generate architecture diagrams.
            - Do NOT add extra sections beyond the 5 listed.
            - Do NOT explain your reasoning.
            - Do NOT add comments, tips, or additional markdown outside the 5 sections.
            - Focus on being concise but informative.
            - Only output pure markdown content for the README.md file.

            """
        ),
        (
            "user", 
            """Given the following codebase context:
            
            {context}
            """
        )
    ])


    chain = prompt | model
    readme = chain.invoke({"context": full_context}).content
    with open(f"testing_readmes/testing_README_{str(idx)}.md", "w") as f:
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


    paths = [ 
        "/Users/demonicaoi/Documents/MERN-Stack",
        "/Users/demonicaoi/Documents/beginner-projects",
        "/Users/demonicaoi/Documents/gitdiagram",
        "/Users/demonicaoi/Documents/EcommerceApp"
    ]
    for idx in range(len(paths)):
        vector_store.reset_collection()
        resultant_files = scan_subfolders(path=paths[idx])
        read_files = read_contents(resultant_files)
        documents, uuids = read_all_file_contents(read_files)
        vector_store.add_documents(documents)
        generate_readme_with_rag(vector_store, model,idx)
