import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from models.schemas import CommitAnalysis, CommitGroup
from tools.git_tools import get_diff

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
    console.print(f"[bold green]✓[/bold green] {message}")

def print_error(message: str):
    console.print(f"[bold red]✗[/bold red] {message}")
    
def print_warning(message: str):
    console.print(f"[bold yellow]![/bold yellow] {message}")

def display_single_proposal(analysis: CommitAnalysis):
    console.print("\n[bold cyan]╭────────────────────────────────────────────╮[/bold cyan]")
    console.print("[bold cyan]│ Suggested Commit                           │[/bold cyan]")
    console.print("[bold cyan]├────────────────────────────────────────────┤[/bold cyan]")
    
    scope_str = f"({analysis.scope})" if analysis.scope else ""
    header = f"{analysis.commit_type}{scope_str}: {analysis.subject}"
    
    console.print(f"  [bold white]{header}[/bold white]\n")
    
    for para in analysis.body:
        console.print(f"  {para}")
    
    console.print("[bold cyan]╰────────────────────────────────────────────╯[/bold cyan]\n")
    
    console.print(f"[bold]Intent:[/bold]\n{analysis.intent}\n")
    console.print(f"[bold]Confidence:[/bold]\n{int(analysis.confidence * 100)}%\n")

def display_multiple_proposal(analysis: CommitAnalysis):
    console.print("\n[bold cyan]╭────────────────────────────────────────────╮[/bold cyan]")
    console.print("[bold cyan]│ Suggested Commits (Multiple)               │[/bold cyan]")
    console.print("[bold cyan]├────────────────────────────────────────────┤[/bold cyan]")
    
    for i, group in enumerate(analysis.groups, 1):
        scope_str = f"({group.scope})" if group.scope else ""
        header = f"{group.commit_type}{scope_str}: {group.subject}"
        
        console.print(f"  [bold yellow]Commit {i}:[/bold yellow] [bold white]{header}[/bold white]")
        for para in group.body:
            console.print(f"    {para}")
        console.print(f"    [dim]Files: {', '.join(group.files)}[/dim]\n")
        
    console.print("[bold cyan]╰────────────────────────────────────────────╯[/bold cyan]\n")
    
    console.print(f"[bold]Intent:[/bold]\n{analysis.intent}\n")
    console.print(f"[bold]Confidence:[/bold]\n{int(analysis.confidence * 100)}%\n")
    print_warning("Note: Multiple commits can only be auto-executed if file groups are completely disjoint.")

def prompt_approval() -> str:
    console.print("\n[bold][A] Approve  [E] Edit  [R] Regenerate  [D] Show Diff  [C] Cancel[/bold]")
    choice = Prompt.ask("Action", choices=["A", "a", "E", "e", "R", "r", "D", "d", "C", "c"], default="A")
    return choice.upper()

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
    console.print("\n[bold cyan]Staged Diff:[/bold cyan]")
    staged = get_diff(staged=True)
    if staged:
        console.print(staged)
    else:
        console.print("[dim]No staged changes.[/dim]")
        
    console.print("\n[bold cyan]Unstaged Diff:[/bold cyan]")
    unstaged = get_diff(staged=False)
    if unstaged:
        console.print(unstaged)
    else:
        console.print("[dim]No unstaged changes.[/dim]")
