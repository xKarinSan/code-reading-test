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


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(openai_api_key=api_key)

def read_and_summarize_all_files(read_files, model, max_workers=6):
    """
    Read files, summarize their content, and return summarized Document objects.
    Each Document will have the summarized content as page_content and metadata attached.
    """
    print(f"[⚡️] Reading and summarizing {len(read_files)} files in parallel...")

    summarization_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a software engineer summarizing source code for internal documentation. "
            "You need to retain key technical elements without formatting it for internal use."
        ),
        (
            "user",
            """Summarize the following file while keeping all important implementation details.

            Include:
            - All function and class definitions (keep signatures and bodies)
            - Import statements
            - Core logic (retain control flow and important operations)
            - All environment variable usage (e.g., os.getenv, os.environ, process.env)

            Ignore:
            - Docstrings
            - Markdown formatting
            - Unnecessary comments

            You may simplify some repeated logic, but do not omit anything important.

            --- FILE START ---

            {code}

            --- FILE END ---"""
        )
    ])

    chain = summarization_prompt | model

    summarized_documents = []
    uuids = []

    def summarize_file(file_obj, file_id):
        content = file_obj["contents"].strip()
        if len(content) <= 50:
            return None
        summary = chain.invoke({"code": content}).content
        return Document(
            page_content=f"File: {file_obj['filePath']}\n{summary.strip()}",
            metadata={
                "source": file_obj["filePath"],
                "extension": file_obj["extension"],
                "id": file_id,
            }
        )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(summarize_file, file, idx): file
            for idx, file in enumerate(read_files)
        }
        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                summarized_documents.append(result)
                uuids.append(str(uuid4()))

    print(f"[✅] Summarized {len(summarized_documents)} files successfully.")
    return summarized_documents, uuids
