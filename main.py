import asyncio
import time
import os

from langchain_ollama.llms import OllamaLLM
from langchain.chat_models import ChatOpenAI 
from dotenv import load_dotenv

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser

from templates import inline_doc_templates, user_template
from files import scan_subfolders, read_contents

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# model = OllamaLLM(model="llama3.2:1b",keep_alive=True,top_k=1)
model = ChatOpenAI(openai_api_key = api_key)



def read_all_file_contents():
    return
    

if __name__ == "__main__":
    print("[🔍] Scanning files...")
    start = time.time()

    resultant_files = scan_subfolders()
    read_files = read_contents(resultant_files)
    
    