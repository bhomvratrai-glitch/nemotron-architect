import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from nemotron_architect.agent import NemotronArchitectAgent
from nemotron_architect.config import config

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="Nemotron-Architect: Autonomous Self-Healing AI Engineer (Powered by NVIDIA Nemotron & Nebius)"
    )
    parser.add_argument("prompt", nargs="?", default="Create an in-memory rate limiter with token bucket algorithm and unit tests", help="Prompt or task for the agent to build")
    parser.add_argument("--output", "-o", default="./generated_project", help="Directory where verified project will be written")
    parser.add_argument("--web", action="store_true", help="Launch the Nemotron-Architect Web Studio UI")
    args = parser.parse_args()

    if args.web:
        from nemotron_architect.server import start_server
        start_server()
        return

    console.print(
        Panel.fit(
            "[bold cyan]⚡ Nemotron-Architect[/bold cyan] [dim]|[/dim] [green]NVIDIA Nemotron 70B[/green] + [yellow]Nebius Token Factory[/yellow]\n"
            "[white]Autonomous Self-Healing Software Engineering Engine[/white]",
            border_style="cyan"
        )
    )

    console.print(f"[bold yellow]🎯 Mission Prompt:[/bold yellow] [white]{args.prompt}[/white]")
    console.print(f"[bold yellow]📁 Output Dir:[/bold yellow] [cyan]{args.output}[/cyan]\n")

    def log_handler(msg: str):
        console.print(f"[dim]{msg}[/dim]")

    agent = NemotronArchitectAgent(on_log=log_handler)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Orchestrating Nemotron Agent Pipeline...", total=None)
        report = agent.run(user_prompt=args.prompt, output_dir=args.output)

    # Render summary table
    table = Table(title="🏗️ Build & Verification Report", border_style="green" if report.success else "red")
    table.add_column("Property", style="bold")
    table.add_column("Status / Value")

    table.add_row("Status", "[bold green]100% VERIFIED & PASSED[/bold green]" if report.success else "[bold red]FAILED[/bold red]")
    table.add_row("Files Generated", str(len(report.files)))
    table.add_row("Self-Heal Cycles", str(report.heal_attempts))
    table.add_row("Tavily Live References", str(len(report.research_summary)))
    table.add_row("Output Location", str(Path(args.output).resolve()))

    console.print(table)

    if report.test_results:
        console.print(Panel(
            report.test_results.stdout if report.test_results.stdout else (report.test_results.stderr or "Clean test run"),
            title="🧪 Test Suite Output",
            border_style="green" if report.success else "red"
        ))

    sys.exit(0 if report.success else 1)

if __name__ == "__main__":
    main()
