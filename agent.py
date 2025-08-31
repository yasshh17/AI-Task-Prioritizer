import os
import json
import datetime
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress

console = Console()
load_dotenv()

# --- 1. Setup Groq client ---
try:
    groq_api_key = os.environ["GROQ_API_KEY"]
    client = Groq(api_key=groq_api_key)
except KeyError:
    console.print("[bold red]ERROR: GROQ_API_KEY not found. Please check your .env file.[/bold red]")
    exit()


# --- 2. Core AI function ---
def get_ai_prioritization(tasks: list[str], goal: str) -> str | None:
    system_prompt = """
    You are an expert productivity coach. Prioritize the given list of tasks
    according to the user's main goal. Respond ONLY with valid JSON:
    {
      "prioritized_tasks": [
         {"task": "...", "priority": "High/Medium/Low", "reason": "..."}
      ]
    }
    """
    task_list_str = "\n".join(f"- {task}" for task in tasks)
    user_prompt = f"My main goal today is: \"{goal}\".\n\nHere are my tasks:\n{task_list_str}"

    try:
        with console.status("[bold blue]AI is analyzing your tasks...[/bold blue]"):
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
                response_format={"type": "json_object"},
            )
        return chat_completion.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        return None


# --- 3. Display AI results ---
def display_results(data: dict, save=True):
    task_list = data.get("prioritized_tasks", [])

    if not task_list:
        console.print("[yellow]No tasks found in AI response.[/yellow]")
        return

    table = Table(title="Your AI-Prioritized Task List", show_header=True, header_style="bold blue")
    table.add_column("Done", width=6)
    table.add_column("Priority", width=10)
    table.add_column("Task", style="bold green")
    table.add_column("Justification")

    priority_styles = {"High": "bold red", "Medium": "bold yellow", "Low": "bold cyan"}
    for idx, task in enumerate(task_list, start=1):
        status = "✅" if task.get("done", False) else "❌"
        priority = task.get("priority", "N/A")
        style = priority_styles.get(priority, "white")
        table.add_row(status, f"[{style}]{priority}[/{style}]", task.get("task", ""), task.get("reason", ""))

    console.print(table)

    if save:
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"tasks_{today}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        with open("latest.json", "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"✓ [green]Progress saved to {filename} and latest.json[/green]")


# --- 4. Load saved results ---
def load_previous_results():
    if os.path.exists("latest.json"):
        with open("latest.json", "r") as f:
            return json.load(f)
    return None


# --- 5. Task completion tracker ---
def mark_task_complete(data: dict):
    tasks = data.get("prioritized_tasks", [])
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return data

    while True:
        display_results(data, save=False)

        # Count completed vs total
        done_count = sum(1 for t in tasks if t.get("done", False))
        total_count = len(tasks)
        console.print(f"\n[bold green]{done_count}/{total_count} tasks completed[/bold green]")

        choice = Prompt.ask("\nEnter task number to toggle complete, or press Enter to stop", default="")
        if not choice.strip():
            break
        if choice.isdigit() and 1 <= int(choice) <= len(tasks):
            idx = int(choice) - 1
            tasks[idx]["done"] = not tasks[idx].get("done", False)
        else:
            console.print("[red]Invalid choice.[/red]")

    return data


# --- 6. Main Menu ---
def main():
    console.print(Panel("[bold green]AI Personal Task Prioritizer[/bold green]", expand=False, border_style="blue"))

    console.print("\n[bold]Menu:[/bold]")
    console.print("1. Create a new prioritized task list")
    console.print("2. Load your last session")
    console.print("3. Track progress (mark tasks complete)")
    console.print("4. Exit")

    choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])

    if choice == "1":
        goal = Prompt.ask("\n[bold]What is your single most important goal for today?[/bold]")
        tasks = []
        console.print("\nEnter your tasks one by one.")
        console.print("Type 'done' or press Enter with no text to finish.")
        while True:
            task = Prompt.ask("  ↳ Task")
            if not task.strip() or task.lower().strip(" '\"") == "done":
                break
            if task not in tasks:  # avoid duplicates
                tasks.append(task)

        if not tasks:
            console.print("[yellow]No tasks entered. Exiting.[/yellow]")
            return

        ai_response_json = get_ai_prioritization(tasks, goal)
        if ai_response_json:
            console.print("\n[bold green]✓ Analysis Complete![/bold green]")
            data = json.loads(ai_response_json)
            # initialize "done" field
            for t in data["prioritized_tasks"]:
                t["done"] = False
            display_results(data)

    elif choice == "2":
        prev = load_previous_results()
        if prev:
            console.print("\n[bold green]✓ Loaded last session[/bold green]")
            display_results(prev, save=False)
        else:
            console.print("[yellow]No previous session found.[/yellow]")

    elif choice == "3":
        prev = load_previous_results()
        if prev:
            prev = mark_task_complete(prev)
            display_results(prev)
        else:
            console.print("[yellow]No session found to track progress.[/yellow]")

    elif choice == "4":
        console.print("[bold red]Goodbye![/bold red]")
        exit()


if __name__ == "__main__":
    main()
