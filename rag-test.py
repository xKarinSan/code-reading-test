import os

from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI 
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_core.runnables import Runnable

from dotenv import load_dotenv

from langchain.prompts.chat import ChatPromptTemplate

from templates import inline_doc_templates, user_template
from files import scan_subfolders, read_contents
from uuid import uuid4

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# model = OllamaLLM(model="llama3.2:1b",keep_alive=True,top_k=1)
model = ChatOpenAI(openai_api_key = api_key)

def read_all_file_contents(read_files):
    """
    Convert the files into documents
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
def generate_readme_with_rag(vector_store, model):
    print("[📚] Retrieving relevant content for README.md...")
    
    all_docs = vector_store.get(include=["documents", "metadatas"])
    all_texts = all_docs["documents"]

    print(f"[📦] Loaded {len(all_texts)} documents from vector DB")

    # Join all file contents together (as a single prompt context)
    full_context = "\n\n".join(all_texts)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert software engineer who writes clean, production-ready README.md files for codebases."
        ),
        (
            "user",
            """Given the following codebase context:

            {context}

            Generate a professional README.md file with the following sections:

            1. **Project Description** – Explain what the project does and its purpose.
            2. **Tech Stack** – List the programming languages, libraries, and frameworks used.
            3. **Environment Variables** – Mention any environment variables required (e.g., API keys, DB configs).
            4. **Setup Instructions** – Include steps to install dependencies and set up the environment.
            5. **Running Instructions** – Provide commands or steps to run the project locally or in production.

            Make sure the README is structured clearly using markdown syntax and is concise but informative.
            """
                )
            ])

    chain = prompt | model
    readme = chain.invoke({"context": full_context}).content

    with open("README.md", "w") as f:
        f.write(readme)

    print("[✅] README.md generated using full context (no limit).")
    
if __name__ == "__main__":
    print("[🔍] Scanning files...")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Chroma(
        collection_name="codebase_name",
        embedding_function=embeddings,
        persist_directory="./vector_db",  # Where to save data locally, remove if not necessary
    )
    curr_path = "/Users/demonicaoi/Documents/MERN-Stack"

    resultant_files = scan_subfolders(path=curr_path)
    for file in resultant_files:
        print("file: ",file)
    
    read_files = read_contents(resultant_files)
    # print("read_files \n",read_files)
    documents, uuids = read_all_file_contents(read_files)
    # print(documents)
    vector_store.add_documents(documents)
    generate_readme_with_rag(vector_store, model)

    
    