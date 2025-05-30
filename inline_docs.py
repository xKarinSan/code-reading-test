import asyncio
import time
import os

from langchain_ollama.llms import OllamaLLM
from langchain.chat_models import ChatOpenAI 
from dotenv import load_dotenv

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser

from files import scan_subfolders, read_contents
from templates import inline_doc_templates, user_template

from const import paths

class SimpleOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text.strip()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# model = OllamaLLM(model="llama3.2:1b",keep_alive=True,top_k=1)
model = ChatOpenAI(openai_api_key = api_key)

# Async function to process a single file
def process_file(file_path: str, code: str, extension: str):
    print(f"[✏️] Documenting: {file_path} ({extension})")
    prompt = ChatPromptTemplate.from_template(inline_doc_templates + "\n\n" + user_template)
    chain = prompt | model | SimpleOutputParser()
    
    try:
        result = chain.invoke({"code": code, "language": extension})
        full_path = "./doc_results/"+file_path
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            print("result")
            f.write(result)
        print(f"[✅] Finished: {file_path}")
    except Exception as e:
        print(f"[❌] Error processing {file_path}: {e}")

# Run all file processes in parallel
async def run_all(read_files: list):
    # MAX_CONCURRENT_TASKS = 3
    # semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    async def wrapped(file):
        # async with semaphore:
        await asyncio.to_thread(process_file, file["filePath"], file["contents"], file["extension"])
    tasks = [wrapped(file) for file in read_files]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("[🔍] Scanning files...")
    start = time.time()

    for idx in range(len(paths)):

        resultant_files = scan_subfolders(path=paths[idx])
        read_files = read_contents(resultant_files)
        print(f"[📄] Found {len(read_files)} files to document.\n")
        asyncio.run(run_all(read_files))
        print(f"\n[🎉] Documentation completed in {time.time() - start:.2f}s")
    