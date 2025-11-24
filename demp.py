from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
client = genai.Client()

store = client.file_search_stores.create()

upload_op = client.file_search_stores.upload_to_file_search_store(
    file_search_store_name=store.name,
    file="D:\VsCode\Chatbot_resume\Deepkothari_Resume.pdf",
)

print("Store ID:", store.name)
