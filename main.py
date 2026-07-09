import typer
from agent.commit_agent import CommitAgent

app = typer.Typer(help="Commitra: Agentic AI Git Commit CLI")

@app.command()
def main():
    """Run the interactive Agentic AI Git commit workflow."""
    agent = CommitAgent()
    agent.run()

@app.command()
def analyze():
    """Analyze the repository changes without committing."""
    typer.echo("Analysis only mode is not yet fully implemented. Running main workflow...")
    agent = CommitAgent()
    agent.run()

if __name__ == "__main__":
    app()
