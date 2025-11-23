from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm_gpt = ChatOpenAI(model="gpt-4o-mini")
