import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from models.schemas import CommitAnalysis, CommitGroup, RepoContext
from tools.git_tools import get_diff, get_file_diff, get_diff_stats

console = Console()

def display_banner():
    banner = Panel.fit(
        "[bold cyan]Commitra[/bold cyan]\n[dim]Agentic AI Git Commit CLI[/dim]",
        border_style="cyan"
    )
    console.print(banner)
    console.print()

def print_step(step_num: int, total_steps: int, message: str):
    console.print(f"[bold blue][{step_num}/{total_steps}][/bold blue] {message}")

def print_success(message: str):
    console.print(f"[bold green][OK][/bold green] {message}")

def print_error(message: str):
    console.print(f"[bold red][X][/bold red] {message}")
    
def print_warning(message: str):
    console.print(f"[bold yellow]![/bold yellow] {message}")

def display_repo_summary(context: RepoContext):
    console.print("\n[bold]Repository[/bold]")
    console.print("────────────────────────────────────────")
    console.print(f"Branch       {context.branch}")
    
    staged_count = sum(1 for f in context.changed_files if f.staged)
    unstaged_count = sum(1 for f in context.changed_files if not f.staged)
    
    unique_files = list(set(f.path for f in context.changed_files))
    console.print(f"Changes      {len(unique_files)} files")
    console.print(f"Staged       {staged_count}")
    console.print(f"Unstaged     {unstaged_count}\n")
    
    for f in context.changed_files:
        console.print(f"{f.status[0].upper():<2} {f.path}")
    console.print()

def display_single_proposal(analysis: CommitAnalysis):
    console.print("\n[bold cyan]╭──────────────────── Proposed commit ────────────────────╮[/bold cyan]")
    console.print("│                                                         │")
    scope_str = f"({analysis.scope})" if analysis.scope else ""
    header = f"{analysis.commit_type}{scope_str}: {analysis.subject}"
    console.print(f"│  1  [bold white]{header}[/bold white]")
    console.print("│                                                         │")
    for para in analysis.body:
        console.print(f"│     • {para}")
    console.print("│                                                         │")
    console.print("[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]\n")
    
    console.print(f"[bold]Intent:[/bold]\n{analysis.intent}\n")
    console.print(f"[bold]Confidence:[/bold]\n{int(analysis.confidence * 100)}%\n")

def display_multiple_proposal(analysis: CommitAnalysis):
    console.print("\n[bold cyan]╭──────────────────── Proposed commits ────────────────────╮[/bold cyan]")
    console.print("│                                                         │")
    for i, group in enumerate(analysis.groups, 1):
        scope_str = f"({group.scope})" if group.scope else ""
        header = f"{group.commit_type}{scope_str}: {group.subject}"
        
        console.print(f"│  {i}  [bold white]{header}[/bold white]")
        console.print("│                                                         │")
        for para in group.body:
            console.print(f"│     • {para}")
        console.print("│                                                         │")
        console.print("│     [dim]Files[/dim]")
        for f in group.files:
            console.print(f"│     [dim]{f}[/dim]")
        console.print("│                                                         │")
        
    console.print("[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]\n")
    
    console.print(f"[bold]Intent:[/bold]\n{analysis.intent}\n")
    console.print(f"[bold]Confidence:[/bold]\n{int(analysis.confidence * 100)}%\n")
    print_warning("Note: Multiple commits can only be auto-executed if file groups are completely disjoint.")

def prompt_approval() -> str:
    console.print("\n[bold]What do you want to do?[/bold]\n")
    console.print("1. Approve commits")
    console.print("2. Edit proposal")
    console.print("3. Regenerate")
    console.print("4. View changes")
    console.print("5. Cancel\n")
    
    choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5"], default="1")
    mapping = {"1": "A", "2": "E", "3": "R", "4": "D", "5": "C"}
    return mapping[choice]

def prompt_edit_single(analysis: CommitAnalysis):
    console.print("\n[bold yellow]Editing Subject:[/bold yellow]")
    scope_str = f"({analysis.scope})" if analysis.scope else ""
    current_subject = f"{analysis.commit_type}{scope_str}: {analysis.subject}"
    new_subject = Prompt.ask("Subject", default=current_subject)
    
    console.print("\n[bold yellow]Editing Body (comma separated, or leave blank to keep current, type 'none' to clear):[/bold yellow]")
    current_body = " | ".join(analysis.body)
    new_body = Prompt.ask("Body", default=current_body)
    
    # We will just treat the new subject as the full header (type + scope + subject)
    # The actual implementation of git commit will use it directly.
    # To keep it simple, we modify the analysis object in place.
    # But wait, how do we decouple the type/scope/subject now? 
    # For a simple MVP edit, we can just shove everything into subject and clear body.
    analysis.subject = new_subject
    analysis.commit_type = "" 
    analysis.scope = ""
    
    if new_body.strip().lower() == "none":
        analysis.body = []
        
    elif new_body != current_body:
        analysis.body = [p.strip() for p in new_body.split("|") if p.strip()]

def prompt_feedback() -> str:
    return Prompt.ask("\n[bold yellow]Regeneration feedback[/bold yellow]")

def display_diff():
    stats = get_diff_stats()
    if not stats:
        console.print("[dim]No diff stats available.[/dim]")
        return
        
    files = list(stats.keys())
    while True:
        console.print("\n[bold cyan]╭──────────────────── Changed files ─────────────────────╮[/bold cyan]")
        for i, filepath in enumerate(files, 1):
            added = stats[filepath].get("added", 0)
            removed = stats[filepath].get("removed", 0)
            line = f"│  {i}. {filepath}"
            pad = 42 - len(line)
            if pad < 1: pad = 1
            line += " " * pad + f"+{added:<3} -{removed:<3} │"
            console.print(line)
        console.print("[bold cyan]╰────────────────────────────────────────────────────────╯[/bold cyan]\n")
        
        console.print("Select a file to inspect (or 'B' to Back):")
        choices = [str(i) for i in range(1, len(files) + 1)] + ["B", "b"]
        choice = Prompt.ask("File", choices=choices)
        if choice.upper() == "B":
            break
            
        idx = int(choice) - 1
        selected_file = files[idx]
        console.print(f"\n[bold yellow]--- Diff for {selected_file} ---[/bold yellow]")
        console.print(get_file_diff(selected_file))
