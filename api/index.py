import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class TaskRequest(BaseModel):
    goal: str
    tasks: List[str]

@app.post("/api/prioritize")
async def prioritize_tasks(request: TaskRequest):
    system_prompt = """You are an expert productivity coach. Return a JSON object with "prioritized_tasks" array containing objects with "task", "priority" (High/Medium/Low), "reason", and "done" (false) fields."""
    
    prompt = f"Goal: {request.goal}\nTasks: {', '.join(request.tasks)}"
    
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    return json.loads(completion.choices[0].message.content)