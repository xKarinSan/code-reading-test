import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.prompts.chat import ChatPromptTemplate

from files import scan_subfolders, read_contents
from rag_test import read_and_summarize_all_files


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def generate_readme_with_rag(vector_store, model,index):
    print("[📚] Retrieving all content from vector DB for summarization...")
    all_docs = vector_store.get(include=["documents", "metadatas"])
    all_texts = all_docs["documents"]
    all_metas = all_docs["metadatas"]

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
    filtered_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(all_texts, all_metas)
        if Path(meta["source"]).suffix in key_extensions
    ]

    # Optional: reduce further to top 15 largest files
    full_context = "\n".join(doc.page_content for doc in filtered_docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert software engineer who writes clean, production-ready README.md files for codebases."),
        ("user", """Given the following codebase context:

{context}

Generate a professional README.md file with the following sections:

1. **Project Description** – Explain what the project does and its purpose.
2. **Tech Stack** – List the programming languages, libraries, and frameworks used.
3. **Environment Variables** – Mention any environment variables required (e.g., API keys, DB configs).
4. **Setup Instructions** – Include steps to install dependencies and set up the environment.
5. **Running Instructions** – Provide commands or steps to run the project locally or in production.

Use clean, minimal markdown. Be succinct. Do not include unnecessary details.
""")
    ])

    chain = prompt | model
    readme = chain.invoke({"context": full_context}).content


    with open(f"testing_readmes/testing_README{str(index)}.md", "w") as f:
        f.write(readme)
        

if __name__ == "__main__":
    print("[🔍] Scanning files...")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Chroma(
        collection_name="codebase_name",
        embedding_function=embeddings,
        persist_directory="./vector_db")
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
        documents, uuids = read_and_summarize_all_files(read_files,model)
        vector_store.add_documents(documents)
        generate_readme_with_rag(vector_store, model,idx)
