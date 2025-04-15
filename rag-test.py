import os
from pathlib import Path
from uuid import uuid4


from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.prompts.chat import ChatPromptTemplate

from files import scan_subfolders, read_contents

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def read_all_file_contents(read_files):
    """
    Convert the files into LangChain Document objects.
    """
    documents = []
    id = 0
    for file in read_files:
        new_doc = Document(
            page_content=file["contents"],
            metadata={
                "source": file["filePath"],
                "extension": file["extension"],
                "id": id,
            },
        )
        id += 1
        documents.append(new_doc)
    uuids = [str(uuid4()) for _ in range(len(documents))]
    return documents, uuids


def summarize_documents(docs, model, max_workers=6):
    """
    Summarize each file concurrently to reduce total token usage and speed up processing.
    """
    print(f"[⚡️] Summarizing {len(docs)} documents in parallel...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a software engineer summarizing source code for documentation purposes."),
        ("user", "Summarize this file:\n\n{code}")
    ])
    chain = prompt | model

    summaries = []

    def summarize_doc(doc):
        content = doc.page_content.strip()
        if len(content) <= 50:
            return None
        summary = chain.invoke({"code": content}).content
        return f"File: {doc.metadata['source']}\n{summary}\n"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_doc = {executor.submit(summarize_doc, doc): doc for doc in docs}
        for future in as_completed(future_to_doc):
            result = future.result()
            if result:
                summaries.append(result)

    return summaries
def generate_readme_with_rag(vector_store, model):
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
    # filtered_docs = sorted(filtered_docs, key=lambda d: -len(d.page_content))[:15]

    summaries = summarize_documents(filtered_docs, model)
    full_context = "\n".join(summaries)
    print(full_context)

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

Use clean markdown formatting and keep it concise but informative.
""")
    ])

    chain = prompt | model
    readme = chain.invoke({"context": full_context}).content

    with open("testing_README.md", "w") as f:
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

    generate_readme_with_rag(vector_store, model)
