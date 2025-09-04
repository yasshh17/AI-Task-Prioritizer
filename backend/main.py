import os
import json
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Task Prioritizer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
try:
    groq_api_key = os.environ["GROQ_API_KEY"]
    client = Groq(api_key=groq_api_key)
except KeyError:
    raise Exception("GROQ_API_KEY not found in environment variables")

# Pydantic models for request/response validation
class TaskRequest(BaseModel):
    goal: str
    tasks: List[str]

class PrioritizedTask(BaseModel):
    task: str
    priority: str
    reason: str
    done: bool = False

class TaskResponse(BaseModel):
    prioritized_tasks: List[PrioritizedTask]

class SaveRequest(BaseModel):
    prioritized_tasks: List[PrioritizedTask]

class UpdateTaskRequest(BaseModel):
    task_index: int
    done: bool

# Storage directory
STORAGE_DIR = "data"
LATEST_FILE = f"{STORAGE_DIR}/latest.json"

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def get_ai_prioritization(tasks: List[str], goal: str) -> Optional[str]:
    """Get task prioritization from Groq AI model."""
    system_prompt = """
    You are an expert productivity coach. Your job is to prioritize a list of tasks
    based on a user's primary goal. Analyze the tasks and the goal, then
    return a JSON object. This object should contain a single key "prioritized_tasks",
    which is an array of objects. Each object must have three string fields:
    "task", "priority" (High, Medium, or Low), and "reason".
    Your response must ONLY be the valid JSON object.
    """
    
    task_list_str = "\n".join(f"- {task}" for task in tasks)
    user_prompt = f"My main goal today is: \"{goal}\"\n\nHere are my tasks:\n{task_list_str}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI API error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"message": "AI Task Prioritizer API is running"}

@app.post("/api/prioritize", response_model=TaskResponse)
async def prioritize_tasks(request: TaskRequest):
    """Prioritize tasks based on the user's goal."""
    if not request.tasks:
        raise HTTPException(status_code=400, detail="No tasks provided")
    
    ai_response = get_ai_prioritization(request.tasks, request.goal)
    if not ai_response:
        raise HTTPException(status_code=500, detail="Failed to get AI response")
    
    try:
        data = json.loads(ai_response)
        # Add done field to each task
        for task in data["prioritized_tasks"]:
            task["done"] = False
        return TaskResponse(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid AI response format")

@app.post("/api/save")
async def save_tasks(request: SaveRequest):
    """Save prioritized tasks to storage."""
    try:
        # Save with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        timestamped_file = f"{STORAGE_DIR}/tasks_{timestamp}.json"
        
        data = {"prioritized_tasks": [task.dict() for task in request.prioritized_tasks]}
        
        # Save timestamped version
        with open(timestamped_file, "w") as f:
            json.dump(data, f, indent=2)
        
        # Save as latest
        with open(LATEST_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        return {"message": "Tasks saved successfully", "filename": timestamped_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save tasks: {str(e)}")

@app.get("/api/load", response_model=TaskResponse)
async def load_tasks():
    """Load the last saved session."""
    try:
        if not os.path.exists(LATEST_FILE):
            raise HTTPException(status_code=404, detail="No saved session found")
        
        with open(LATEST_FILE, "r") as f:
            data = json.load(f)
        
        return TaskResponse(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid saved data format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load tasks: {str(e)}")

@app.put("/api/tasks/{task_index}")
async def update_task_status(task_index: int, request: UpdateTaskRequest):
    """Update the completion status of a specific task."""
    try:
        if not os.path.exists(LATEST_FILE):
            raise HTTPException(status_code=404, detail="No saved session found")
        
        with open(LATEST_FILE, "r") as f:
            data = json.load(f)
        
        tasks = data.get("prioritized_tasks", [])
        if task_index < 0 or task_index >= len(tasks):
            raise HTTPException(status_code=400, detail="Invalid task index")
        
        tasks[task_index]["done"] = request.done
        
        # Save updated data
        with open(LATEST_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        return {"message": "Task status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")

# IMPORTANT: Mount static files AFTER all API routes are defined
# This ensures API routes are matched first before falling back to static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)