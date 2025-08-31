import os
import json
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.table import Table

# --- INITIALIZATION ---
# Initialize the Rich Console for beautiful output in your terminal
console = Console()

# Load environment variables from .env file
load_dotenv()

# Try to get the Groq API key from environment variables
try:
    groq_api_key = os.environ["GROQ_API_KEY"]
    client = Groq(api_key=groq_api_key)
except KeyError:
    console.print("[bold red]ERROR: GROQ_API_KEY not found in .env file.[/bold red]")
    exit()

# --- AGENT LOGIC (This function does not need to change) ---
def get_ai_prioritization(tasks: list[str], goal: str) -> str | None:
    """
    Gets task prioritization from the Groq AI model.
    """
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
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]An error occurred with the AI API: {e}[/bold red]")
        return None

# --- NEW: UI & APPLICATION FLOW ---

def display_prioritized_tasks(ai_response_json: str):
    """
    Parses the AI's JSON response and displays it in a beautiful table.
    """
    try:
        # Parse the JSON string into a Python dictionary.
        data = json.loads(ai_response_json)
        task_list = data.get("prioritized_tasks", [])

        if not task_list:
            console.print("[yellow]The AI returned no tasks. Try rephrasing your goal.[/yellow]")
            return

        # Create a table for display using the rich library.
        table = Table(title="Your AI-Prioritized Task List", show_header=True, header_style="bold blue")
        table.add_column("Priority", style="dim", width=10)
        table.add_column("Task", style="bold green")
        table.add_column("Justification")

        # Define styles for different priority levels for a better visual cue.
        priority_styles = {"High": "bold red", "Medium": "bold yellow", "Low": "bold cyan"}

        for task in task_list:
            priority = task.get("priority", "N/A")
            style = priority_styles.get(priority, "white")
            table.add_row(f"[{style}]{priority}[/{style}]", task.get("task", ""), task.get("reason", ""))
        
        console.print(table)

    except json.JSONDecodeError:
        console.print("[bold red]Error: Failed to decode the AI's response.[/bold red]")
        console.print("This can happen if the AI doesn't return perfect JSON. Here is the raw response:")
        console.print(ai_response_json)


def main():
    """The main function to run the interactive command-line interface."""
    # 1. Add a welcome panel for a professional look.
    console.print(Panel("[bold green]AI Personal Task Prioritizer[/bold green]", expand=False, border_style="blue"))
    
    # 2. Get the user's goal for context.
    goal = Prompt.ask("\n[bold]What is your single most important goal for today?[/bold]")
    
    # 3. Collect tasks from the user in a loop.
    tasks = []
    console.print("\nEnter your tasks one by one. Press [Enter] on an empty line when finished.")
    while True:
        task = Prompt.ask("  ↳ Task")
        if not task.strip():
            break
        tasks.append(task)
        
    if not tasks:
        console.print("\n[yellow]No tasks were entered. Exiting.[/yellow]")
        return
        
    # 4. Show a "thinking" spinner while the API call is in progress.
    with console.status("[bold blue]AI is analyzing your tasks...[/bold blue]", spinner="dots"):
        ai_response_json = get_ai_prioritization(tasks, goal)

    # 5. Display the final, formatted results.
    if ai_response_json:
        console.print("\n[bold green]✓ Analysis Complete![/bold green]")
        display_prioritized_tasks(ai_response_json)

if __name__ == "__main__":
    main()