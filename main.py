
from langchain_ollama.llms import OllamaLLM
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser

model = OllamaLLM(model="gemma3")
