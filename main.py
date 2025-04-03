import asyncio

from langchain_ollama.llms import OllamaLLM
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser

from files import scan_subfolders, read_contents
from templates import inline_doc_templates, user_template

class SimpleOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text.strip()

model = OllamaLLM(model="gemma3")

# Async function to process a single file
async def process_file(file_path: str, code: str, extension: str,semaphore: asyncio.Semaphore):
    print(f"[✏️] Documenting: {file_path} ({extension})")
    prompt = ChatPromptTemplate.from_template(inline_doc_templates + "\n\n" + user_template)
    chain = prompt | model | SimpleOutputParser()
    
    try:
        result = await chain.ainvoke({"code": code, "language": extension})
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"[✅] Finished: {file_path}")
    except Exception as e:
        print(f"[❌] Error processing {file_path}: {e}")

# Run all file processes in parallel
async def run_all(read_files: list):
    MAX_CONCURRENT_TASKS = 5
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    tasks = [process_file(file["filePath"], file["contents"],file["extension"],semaphore) for file in read_files]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("[🔍] Scanning files...")
    resultant_files = scan_subfolders()
    read_files = read_contents(resultant_files)
    print(f"[📄] Found {len(read_files)} files to document.\n")
    asyncio.run(run_all(read_files))
    print("\n[🎉] Documentation completed!")
    
    