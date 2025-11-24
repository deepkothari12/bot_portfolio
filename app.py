# import os
# import markdown
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List
# from google import genai 
# from google.genai import types
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware

# load_dotenv()

# ##this the google genai file search store path for the uploaded resume (demp.py)
# RESUME_FILE_PATH =  "fileSearchStores/710bglrg39xn-w0fpkf78edzn" #"D:\\VsCode\\Chatbot_resume\\Deepkothari_Resume.pdf"

# client = genai.Client(
#     ##takes api key from environment variable 'GENAI_API_KEY' automatically
# )
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],           # allow all origins (or specify your frontend)
#     allow_credentials=True,
#     allow_methods=["*"],           # GET, POST, OPTIONS, etc.
#     allow_headers=["*"],           # Content-Type, Authorization, etc.
# )
# # # store = client.file_search_stores.create()
# ## we already create the file store and uplaoded the resume 


# class Questions(BaseModel):
#     questions : str


# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Resume Chatbot API"}



# @app.post("/ask")
# def ask_questions(data: Questions):
#     # print("Received" , Questions.questions)
#     questions = data.questions.strip()

#     if not questions:
#         return {
#             "error" : "Question cannnot be empty"
#         }
    
#     system_prompt = """

#     You are an AI Resume Assistant.
#     You must answer ONLY using information from the user's resume stored in File Search.
#     If the resume does not contain the answer, say:
#     "This information is not available in the resume."
#     Do NOT guess or invent anything.

#     """
#     promt = f"{system_prompt}\n\n User Question: {questions}"


#     try:
#         # print("Sending prompt to Gemini 2.5 Flash model...")
#         response = client.models.generate_content(
#             model='gemini-2.5-flash',
#             contents = promt, 
#             config = types.GenerateContentConfig(
#                     tools=[
#                         types.Tool(
#                             file_search=types.FileSearch(
#                                 file_search_store_names=[RESUME_FILE_PATH]
#                             )
#                         )
#                     ],
#                     temperature=0.2,
#                     # max_output_tokens=300,
#             )
#         )
#         # print(response.text)
#         # print(response.candidates)
#         # print(response['answer']['candidates'])
#         html_markdown_ans = markdown.markdown(response.text)
#         return {
#             "answer" : html_markdown_ans
#         }
    
        
#     except Exception as e:
#         return { "error": str(e)}       

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Generator

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

# This is your existing File Search store name
RESUME_FILE_PATH = "fileSearchStores/710bglrg39xn-w0fpkf78edzn"


client = genai.Client()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Questions(BaseModel):
    questions: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Chatbot API"}


@app.post("/ask")
def ask_questions(data: Questions):
    question = data.questions.strip()

    if not question:
        return {"error": "Question cannot be empty"}

    system_prompt = """
            You are an AI Resume Assistant.

            You must answer ONLY using information from the user's resume stored in File Search.
            If the resume does not contain the answer, say:
            "This information is not available in the resume."
            Do NOT guess or invent anything.

            Format rules:
            - Answer in plain text only.
            - you can use markdown.
            - Do not use bullet points or numbered lists.
            - Do not use bold or italics.
            - give short and concise answers.
            """

    prompt = f"{system_prompt}\n\nUser Question: {question}"

    def stream_response():
        try:
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[RESUME_FILE_PATH]
                            )
                        )
                    ],
                    temperature=0.2,
                ),
            )

            # For each streamed chunk...
            for chunk in response_stream:
                text = (chunk.text or "")
                if not text:
                    continue

                for ch in text:
                    yield ch

        except Exception as e:
            yield f"[Error: {str(e)}]"


    # Return a streaming plain-text response
    return StreamingResponse(stream_response(), media_type="text/plain")
