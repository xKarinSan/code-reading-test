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
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def read_all_file_contents(read_files, chunk_size=500, chunk_overlap=75):
    """
    Convert the files into LangChain Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],  # try to split cleanly: paragraphs > lines > words > chars
    )
    documents = []
    id = 0
    for file in read_files:
        chunks = text_splitter.split_text(file["contents"])
        # chunks = chunk_content(file["contents"], chunk_size)
        for idx, chunk in enumerate(chunks):
            new_doc = Document(
                page_content=chunk,
                metadata={
                    "source": file["filePath"],
                    "extension": file["extension"],
                    "file_chunk_id": idx,
                    "id": id,
                },
            )
            id += 1
            documents.append(new_doc)
    uuids = [str(uuid4()) for _ in range(len(documents))]
    return documents, uuids

# def chunk_content(content, chunk_size=1000):
#     """Split content into chunks of chunk_size characters."""
#     return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
