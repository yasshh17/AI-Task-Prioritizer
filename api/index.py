import os
import json
from http.server import BaseHTTPRequestHandler
from groq import Groq

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get API key
            api_key = os.environ.get('GROQ_API_KEY')
            if not api_key:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "API key not configured"}).encode())
                return
            
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Initialize Groq
            client = Groq(api_key=api_key)
            
            # Create prompt
            system_prompt = """You are an expert productivity coach. Return a JSON object with "prioritized_tasks" array containing objects with "task", "priority" (High/Medium/Low), "reason", and "done" (false) fields."""
            
            tasks_list = data.get('tasks', [])
            goal = data.get('goal', '')
            
            user_prompt = f"Goal: {goal}\nTasks: {', '.join(tasks_list)}"
            
            # Get AI response
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(completion.choices[0].message.content.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = json.dumps({"error": str(e)})
            self.wfile.write(error_msg.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()