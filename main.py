import typer
from agent.commit_agent import CommitAgent

app = typer.Typer(help="Commitra: Agentic AI Git Commit CLI", invoke_without_command=True)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Run the interactive Agentic AI Git commit workflow."""
    if ctx.invoked_subcommand is None:
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
