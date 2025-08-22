"""
Command Line Interface for SpamLevi
Provides interactive and non-interactive modes for spamming operations.
"""

import asyncio
import json
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.panel import Panel
from rich.text import Text

from .core.spam_engine import SpamEngine, TargetManager
from .config.config import Config
from .core.logger import SecurityLogger


console = Console()


class SpamLeviCLI:
    """Interactive CLI handler for SpamLevi."""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine = SpamEngine(config)
        self.logger = SecurityLogger()
        self.target_manager = TargetManager()
    
    async def run_interactive(self):
        """Run the interactive CLI mode."""
        console.print(Panel.fit(
            "[bold blue]SpamLevi - Advanced WhatsApp Spam Tool[/bold blue]\n"
            "[dim]Version 1.0.0 - Use responsibly[/dim]",
            border_style="blue"
        ))
        
        while True:
            choice = await self._show_main_menu()
            
            if choice == "1":
                await self._single_target_mode()
            elif choice == "2":
                await self._file_target_mode()
            elif choice == "3":
                self._show_statistics()
            elif choice == "4":
                self._show_config()
            elif choice == "5":
                console.print("[green]Thank you for using SpamLevi![/green]")
                break
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
    
    async def _show_main_menu(self) -> str:
        """Display the main menu and get user choice."""
        console.print("\n[bold cyan]Main Menu:[/bold cyan]")
        console.print("1. Single Target Mode")
        console.print("2. File Target Mode")
        console.print("3. View Statistics")
        console.print("4. Configuration")
        console.print("5. Exit")
        
        return Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
    
    async def _single_target_mode(self):
        """Handle single target spamming."""
        console.print("\n[bold yellow]Single Target Mode[/bold yellow]")
        
        phone = Prompt.ask("Enter phone number (e.g., +1234567890)")
        message = Prompt.ask("Enter message to send")
        count = IntPrompt.ask("Number of messages to send", default=1)
        delay = FloatPrompt.ask("Delay between messages (seconds)", default=1.0)
        
        if not self.target_manager.validate_phone(phone):
            console.print("[red]Invalid phone number format![/red]")
            return
        
        target = {
            'phone': phone,
            'message': message,
            'count': count,
            'delay': delay
        }
        
        if Confirm.ask(f"Send {count} messages to {phone}?"):
            await self._execute_spam([target])
    
    async def _file_target_mode(self):
        """Handle file-based target spamming."""
        console.print("\n[bold yellow]File Target Mode[/bold yellow]")
        
        file_path = Prompt.ask("Enter path to targets file")
        
        try:
            targets = self.target_manager.load_targets_from_file(file_path)
            if not targets:
                console.print("[red]No valid targets found in file![/red]")
                return
            
            console.print(f"[green]Loaded {len(targets)} targets[/green]")
            
            if Confirm.ask(f"Proceed with {len(targets)} targets?"):
                await self._execute_spam(targets)
                
        except FileNotFoundError:
            console.print(f"[red]File {file_path} not found![/red]")
        except Exception as e:
            console.print(f"[red]Error loading file: {e}[/red]")
    
    async def _execute_spam(self, targets: List[Dict[str, Any]]):
        """Execute spamming with progress display."""
        console.print(f"\n[bold green]Starting spam operation...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Sending messages...", total=len(targets))
            
            try:
                results = await self.engine.spam_multiple_targets(targets)
                
                progress.update(task, completed=len(targets))
                
                # Display results
                self._display_results(results)
                
            except Exception as e:
                console.print(f"[red]Error during spam operation: {e}[/red]")
    
    def _display_results(self, results: Dict[str, Any]):
        """Display spamming results in a table."""
        console.print("\n[bold green]Results:[/bold green]")
        
        table = Table(title="Spam Operation Results")
        table.add_column("Phone", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Sent", justify="right", style="blue")
        table.add_column("Failed", justify="right", style="red")
        
        for phone, result in results.items():
            status = "✓ Success" if result['success'] else "✗ Failed"
            table.add_row(
                phone,
                status,
                str(result['sent']),
                str(result['failed'])
            )
        
        console.print(table)
        
        # Show summary
        stats = self.engine.get_statistics()
        console.print(f"\n[bold]Total sent:[/bold] {stats['total_sent']}")
        console.print(f"[bold]Total failed:[/bold] {stats['total_failed']}")
        console.print(f"[bold]Success rate:[/bold] {stats['success_rate']:.2f}%")
    
    def _show_statistics(self):
        """Display current statistics."""
        stats = self.engine.get_statistics()
        
        console.print("\n[bold cyan]Current Statistics:[/bold cyan]")
        
        stats_table = Table(title="Spam Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        for key, value in stats.items():
            if isinstance(value, float):
                value = f"{value:.2f}"
            stats_table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(stats_table)
    
    def _show_config(self):
        """Display current configuration."""
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]")
        
        config_table = Table(title="Configuration Settings")
        config_table.add_column("Section", style="cyan")
        config_table.add_column("Key", style="yellow")
        config_table.add_column("Value", style="white")
        
        # Rate limit config
        for key, value in self.config.rate_limit.__dict__.items():
            config_table.add_row("Rate Limit", key, str(value))
        
        # Security config
        for key, value in self.config.security.__dict__.items():
            config_table.add_row("Security", key, str(value))
        
        # WhatsApp config
        for key, value in self.config.whatsapp.__dict__.items():
            config_table.add_row("WhatsApp", key, str(value))
        
        console.print(config_table)


async def main(args, config: Config):
    """Main CLI entry point."""
    cli = SpamLeviCLI(config)
    
    if args.single:
        await cli._single_target_mode()
    elif args.file:
        targets = cli.target_manager.load_targets_from_file(args.file)
        if targets:
            await cli._execute_spam(targets)
    else:
        await cli.run_interactive()