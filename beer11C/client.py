#!/usr/bin/env python3
"""
Beer Game CLI Client
====================
A rich terminal client for the Beer Game multiplayer server.
Connects via WebSockets and lets you play from the command line.

Usage:
    python client.py                          # interactive setup
    python client.py --url ws://localhost:8000 --token <your_token>
    python client.py --host localhost --token <your_token>

Requirements:
    pip install websockets rich
"""

import asyncio
import json
import argparse
import sys
from datetime import datetime

try:
    import websockets
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.prompt import Prompt, IntPrompt
    from rich.rule import Rule
    from rich import box
    from rich.columns import Columns
    from rich.align import Align
    from rich.progress import BarColumn, Progress, SpinnerColumn
except ImportError:
    print("Missing dependencies. Run: pip install websockets rich")
    sys.exit(1)

console = Console()

# ── Colours per role ─────────────────────────────────────────────────────────
ROLE_COLORS = {
    'retailer':    'yellow',
    'wholesaler':  'blue',
    'distributor': 'magenta',
    'factory':     'green',
}
ROLE_EMOJIS = {
    'retailer':    '🛒',
    'wholesaler':  '🏪',
    'distributor': '🚚',
    'factory':     '🏭',
}


# ── State ─────────────────────────────────────────────────────────────────────
class GameState:
    def __init__(self, role):
        self.role         = role
        self.week         = 0
        self.max_weeks    = 20
        self.inventory    = 0
        self.backlog      = 0
        self.total_cost   = 0.0
        self.pipeline     = []
        self.history      = []
        self.submitted    = []
        self.connected    = []
        self.has_submitted = False
        self.is_finished  = False
        self.upcoming_demand = None
        self.log          = []   # list of (time, type, message)

    def update_from_state(self, msg):
        self.week         = msg.get('week', self.week)
        self.max_weeks    = msg.get('max_weeks', self.max_weeks)
        self.is_finished  = msg.get('is_finished', False)
        own = msg.get('own', {})
        self.inventory    = own.get('inventory', self.inventory)
        self.backlog      = own.get('backlog', self.backlog)
        self.total_cost   = own.get('total_cost', self.total_cost)
        self.pipeline     = msg.get('pipeline', [])
        self.history      = msg.get('history', [])
        self.submitted    = msg.get('submitted', [])
        self.upcoming_demand = msg.get('upcoming_demand')
        self.has_submitted = False

    def add_log(self, type_, message):
        now = datetime.now().strftime('%H:%M:%S')
        self.log.append((now, type_, message))
        if len(self.log) > 50:
            self.log.pop(0)


# ── Rendering ─────────────────────────────────────────────────────────────────
def render_header(state: GameState) -> Panel:
    role_color = ROLE_COLORS.get(state.role, 'white')
    emoji = ROLE_EMOJIS.get(state.role, '❓')
    title = Text()
    title.append(f"{emoji} ", style="bold")
    title.append(state.role.upper(), style=f"bold {role_color}")
    title.append(f"  |  Week ", style="dim")
    title.append(f"{state.week}", style="bold yellow")
    title.append(f"/{state.max_weeks}", style="dim")
    return Panel(Align.center(title), style="dim")


def render_hud(state: GameState) -> Table:
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t.add_column(justify="center")
    t.add_column(justify="center")
    t.add_column(justify="center")
    if state.role == 'retailer':
        t.add_column(justify="center")

    # Inventory
    inv_color = "green" if state.inventory > 6 else "yellow" if state.inventory > 0 else "red"
    # Backlog
    blg_color = "green" if state.backlog == 0 else "yellow" if state.backlog < 5 else "red"

    row = [
        Panel(Text(f"{state.inventory}", justify="center", style=f"bold {inv_color}") +
              Text("\nINVENTORY", justify="center", style="dim"),
              border_style=inv_color),
        Panel(Text(f"{state.backlog}", justify="center", style=f"bold {blg_color}") +
              Text("\nBACKLOG", justify="center", style="dim"),
              border_style=blg_color),
        Panel(Text(f"${state.total_cost:.1f}", justify="center", style="bold yellow") +
              Text("\nTOTAL COST", justify="center", style="dim"),
              border_style="yellow"),
    ]
    if state.role == 'retailer' and state.upcoming_demand is not None:
        row.append(
            Panel(Text(f"{state.upcoming_demand}", justify="center", style="bold blue") +
                  Text("\nNEXT DEMAND", justify="center", style="dim"),
                  border_style="blue")
        )
    t.add_row(*row)
    return t


def render_pipeline(state: GameState) -> Panel:
    if not state.pipeline:
        return Panel("[dim]No shipments in transit[/dim]", title="📦 Pipeline", border_style="dim")

    t = Table(box=box.SIMPLE_HEAVY, show_header=True)
    t.add_column("Quantity", style="bold white", justify="right")
    t.add_column("Arrives Week", style="yellow", justify="center")
    t.add_column("Weeks Away", justify="center")
    t.add_column("Progress", justify="center", min_width=20)

    for s in state.pipeline:
        weeks_away = s.get('weeks_away', 1)
        bar = "█" * max(0, (2 - weeks_away + 1)) + "░" * weeks_away
        bar_color = "green" if weeks_away == 1 else "yellow"
        t.add_row(
            f"+{s['quantity']} units",
            f"W{s['arrives_week']}",
            f"[{'green' if weeks_away==1 else 'yellow'}]{weeks_away}w[/]",
            f"[{bar_color}]{bar}[/]"
        )
    return Panel(t, title="📦 Incoming Shipments (Pipeline)", border_style="cyan")


def render_player_status(state: GameState) -> Panel:
    roles = ['retailer', 'wholesaler', 'distributor', 'factory']
    parts = []
    for r in roles:
        color = ROLE_COLORS.get(r, 'white')
        emoji = ROLE_EMOJIS.get(r, '')
        if r in state.submitted:
            parts.append(f"[green]✓ {emoji} {r.title()}[/green]")
        elif r in state.connected:
            parts.append(f"[{color}]● {emoji} {r.title()}[/{color}]")
        else:
            parts.append(f"[dim]○ {emoji} {r.title()}[/dim]")
    status = "   ".join(parts)
    waiting = 4 - len(state.submitted)
    subtitle = f"[green]All submitted![/green]" if waiting == 0 else f"[dim]Waiting for {waiting} more…[/dim]"
    return Panel(status + "\n" + subtitle, title="👥 Player Status", border_style="dim")


def render_history(state: GameState) -> Panel:
    if not state.history:
        return Panel("[dim]No history yet[/dim]", title="📈 History", border_style="dim")

    t = Table(box=box.SIMPLE, show_header=True)
    t.add_column("Wk", style="dim", justify="right")
    t.add_column("Inv", justify="right")
    t.add_column("Bklg", justify="right")
    t.add_column("Ordered", justify="right")
    t.add_column("Cost", justify="right")

    recent = state.history[-8:]  # last 8 weeks
    for h in recent:
        inv = h.get('inventory', 0)
        blg = h.get('backlog', 0)
        inv_style = "green" if inv > 0 else "red"
        blg_style = "red" if blg > 0 else "green"
        t.add_row(
            str(h['week']),
            f"[{inv_style}]{inv}[/]",
            f"[{blg_style}]{blg}[/]",
            str(h.get('order_placed', '-')),
            f"${h.get('cost_this_week', 0):.1f}"
        )
    return Panel(t, title="📈 Recent History", border_style="dim")


def render_log(state: GameState, n=6) -> Panel:
    lines = []
    for time_, type_, msg in reversed(state.log[-n:]):
        if type_ == 'system':
            icon, style = "🔌", "dim"
        elif type_ == 'order':
            icon, style = "📤", "cyan"
        elif type_ == 'week':
            icon, style = "📅", "yellow"
        elif type_ == 'error':
            icon, style = "❌", "red"
        else:
            icon, style = "•", "white"
        lines.append(f"[dim]{time_}[/dim] [{style}]{icon} {msg}[/]")
    content = "\n".join(lines) if lines else "[dim]No events yet[/dim]"
    return Panel(content, title="📋 Event Log", border_style="dim")


def render_supply_chain_map(state: GameState) -> Panel:
    """ASCII art supply chain with animated position indicator."""
    roles = ['retailer', 'wholesaler', 'distributor', 'factory']
    nodes = []
    for r in roles:
        color = ROLE_COLORS[r]
        emoji = ROLE_EMOJIS[r]
        if r == state.role:
            nodes.append(f"[bold {color} reverse] {emoji} {r.upper()} [/]")
        elif r in state.submitted:
            nodes.append(f"[green]╔{'═'*10}╗\n║ {emoji} {r[:8].center(8)} ║\n║  ✓ DONE  ║\n╚{'═'*10}╝[/green]")
        elif r in state.connected:
            nodes.append(f"[{color}]┌{'─'*10}┐\n│ {emoji} {r[:8].center(8)} │\n│ ● online │\n└{'─'*10}┘[/]")
        else:
            nodes.append(f"[dim]┌{'─'*10}┐\n│ {emoji} {r[:8].center(8)} │\n│  offline │\n└{'─'*10}┘[/dim]")

    # Build pipeline arrows with truck emoji for in-transit shipments
    arrows = []
    for i, r in enumerate(roles[:-1]):
        has_transit = any(True for s in state.pipeline) if r == state.role else False
        arrow = " 🚚→ " if has_transit and r == state.role else " ──→ "
        arrows.append(arrow)

    # Assemble the row
    row_parts = []
    for i, node in enumerate(nodes):
        row_parts.append(node)
        if i < len(arrows):
            row_parts.append(arrows[i])

    # Simple horizontal layout
    chain = Text()
    chain.append("CUSTOMER ", style="dim")
    chain.append("→ ", style="dim")
    for i, r in enumerate(roles):
        color = ROLE_COLORS[r]
        emoji = ROLE_EMOJIS[r]
        if r == state.role:
            chain.append(f"[{emoji} {r.upper()}]", style=f"bold {color} reverse")
        elif r in state.submitted:
            chain.append(f"✓{r[:4]}", style="green bold")
        elif r in state.connected:
            chain.append(f"●{r[:4]}", style=f"{color}")
        else:
            chain.append(f"○{r[:4]}", style="dim")
        if i < len(roles) - 1:
            # Show truck if this player has pipeline shipments
            chain.append(" 🚚→ " if r == state.role and state.pipeline else " ──→ ", style="dim")

    return Panel(chain, title="🗺  Supply Chain Map", border_style="dim")


def render_ascii_chart(state: GameState, width=50) -> Panel:
    """Mini ASCII bar chart of inventory history."""
    if len(state.history) < 2:
        return Panel("[dim]Waiting for data…[/dim]", title="📊 Inventory Chart", border_style="dim")

    hist = state.history[-width:]
    max_val = max((h.get('inventory', 0) for h in hist), default=1) or 1
    height = 8
    lines = []

    for row in range(height, 0, -1):
        threshold = (row / height) * max_val
        line = ""
        for h in hist:
            inv = h.get('inventory', 0)
            blg = h.get('backlog', 0)
            if blg > 0:
                line += "[red]▼[/red]"
            elif inv >= threshold:
                line += "[green]█[/green]"
            else:
                line += "[dim]·[/dim]"
        lines.append(f"[dim]{int(threshold):3}[/dim] {line}")

    lines.append("[dim]    " + "".join(
        str(h['week'] % 10) for h in hist
    ) + "[/dim]")
    lines.append(f"[dim]     weeks  (last {len(hist)})[/dim]")

    return Panel("\n".join(lines), title="📊 Inventory · [green]█=stock[/green] [red]▼=backlog[/red]",
                 border_style="dim")


def render_full_screen(state: GameState) -> str:
    """Build the complete terminal UI as a renderable."""
    console.clear()
    console.print(render_header(state))
    console.print(render_hud(state))
    console.print(render_supply_chain_map(state))
    console.print(render_pipeline(state))

    # Two-column: chart + status
    console.print(Columns([
        render_ascii_chart(state),
        render_player_status(state),
    ], equal=True))

    console.print(render_history(state))
    console.print(render_log(state))


# ── Command parser ─────────────────────────────────────────────────────────────
def parse_command(raw: str, state: GameState):
    """
    Parse a CLI command and return (ws_message_dict | None, feedback_string).

    Commands:
      order <n>          Submit order of n units
      status             Print current state
      history            Print full history table
      pipeline           Print pipeline details
      help               Show all commands
      quit / exit        Disconnect
    """
    raw = raw.strip()
    if not raw:
        return None, ""

    parts = raw.split()
    cmd = parts[0].lower()

    if cmd in ('order', 'o'):
        if len(parts) < 2:
            return None, "[red]Usage: order <quantity>[/red]"
        try:
            qty = int(parts[1])
            if qty < 0 or qty > 200:
                raise ValueError
        except ValueError:
            return None, "[red]Quantity must be 0–200[/red]"
        if state.has_submitted:
            return None, "[yellow]You already submitted this week.[/yellow]"
        return {'type': 'submit_order', 'quantity': qty}, f"[cyan]Submitting order: {qty} units…[/cyan]"

    elif cmd in ('name', 'n'):
        if len(parts) < 2:
            return None, "[red]Usage: name <your_name>[/red]"
        name = ' '.join(parts[1:])
        return {'type': 'set_name', 'name': name}, f"[cyan]Setting name to: {name}[/cyan]"

    elif cmd in ('status', 's'):
        render_full_screen(state)
        return None, ""

    elif cmd in ('history', 'h'):
        if not state.history:
            return None, "[dim]No history yet.[/dim]"
        t = Table(title="Full History", box=box.MARKDOWN)
        t.add_column("Week"); t.add_column("Inv"); t.add_column("Backlog")
        t.add_column("Ordered"); t.add_column("Rcvd"); t.add_column("Cost"); t.add_column("Cumul.")
        for h in state.history:
            t.add_row(
                str(h['week']), str(h.get('inventory',0)), str(h.get('backlog',0)),
                str(h.get('order_placed',0)), str(h.get('shipment_received',0)),
                f"${h.get('cost_this_week',0):.1f}", f"${h.get('cumulative_cost',0):.1f}"
            )
        console.print(t)
        return None, ""

    elif cmd in ('pipeline', 'p'):
        console.print(render_pipeline(state))
        return None, ""

    elif cmd in ('help', '?'):
        help_text = """
[bold yellow]Available Commands:[/bold yellow]

  [cyan]order <n>[/cyan]      Submit your order for this week (0–200 units)
  [cyan]name <text>[/cyan]    Set your display name
  [cyan]status[/cyan]         Refresh the full game display
  [cyan]history[/cyan]        Print full week-by-week history table
  [cyan]pipeline[/cyan]       Show incoming shipments in detail
  [cyan]help[/cyan]           Show this message
  [cyan]quit[/cyan]           Disconnect from the game

[dim]Shortcuts: o=order, s=status, h=history, p=pipeline[/dim]
        """
        console.print(Panel(help_text.strip(), title="Help", border_style="yellow"))
        return None, ""

    elif cmd in ('quit', 'exit', 'q'):
        return 'QUIT', "[yellow]Disconnecting…[/yellow]"

    else:
        return None, f"[red]Unknown command: '{cmd}'[/red]  Type [cyan]help[/cyan] for commands."


# ── WebSocket client ──────────────────────────────────────────────────────────
async def run_client(ws_url: str, state: GameState):
    console.print(Panel(
        f"[cyan]Connecting to[/cyan] [bold]{ws_url}[/bold]",
        title="🍺 Beer Game CLI",
        border_style="yellow"
    ))

    try:
        async with websockets.connect(ws_url) as ws:
            state.add_log('system', f'Connected to {ws_url}')
            console.print("[green]✓ Connected![/green]")

            # Receive task: handles incoming WS messages
            async def receiver():
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    mtype = msg.get('type')

                    if mtype == 'state_update':
                        state.update_from_state(msg)
                        summary = msg.get('week_summary', {})
                        if summary:
                            state.add_log('week',
                                f"W{state.week} complete — inv:{summary.get('inventory',0)} "
                                f"bklg:{summary.get('backlog',0)} cost:${summary.get('cost_this_week',0):.1f}")
                        render_full_screen(state)
                        if state.is_finished:
                            console.print(Panel(
                                f"[bold yellow]🏁 GAME OVER![/bold yellow]\n"
                                f"Total cost: [bold]${state.total_cost:.1f}[/bold]\n"
                                f"View results at: /game/.../results/",
                                border_style="yellow"
                            ))

                    elif mtype == 'ready_status':
                        state.submitted = msg.get('submitted', [])
                        state.connected = msg.get('connected', [])
                        remaining = 4 - len(state.submitted)
                        if remaining > 0:
                            console.print(f"[dim]⏳ Waiting for {remaining} more player(s) to submit…[/dim]")
                        else:
                            console.print("[green]All submitted! Processing week…[/green]")

                    elif mtype == 'player_joined':
                        msg_text = f"{msg['name']} ({msg['role']}) joined"
                        state.add_log('system', msg_text)
                        console.print(f"[green]→ {msg_text}[/green]")

                    elif mtype == 'player_left':
                        msg_text = f"{msg['name']} ({msg['role']}) left"
                        state.add_log('system', msg_text)
                        console.print(f"[yellow]← {msg_text}[/yellow]")

                    elif mtype == 'error':
                        state.add_log('error', msg['message'])
                        console.print(f"[red]✗ {msg['message']}[/red]")

                    elif mtype == 'game_over':
                        console.print(Panel(
                            f"[bold yellow]🏁 GAME OVER![/bold yellow]\n"
                            f"Results: {msg.get('results_url', 'see browser')}",
                            border_style="yellow"
                        ))

            # Input task: reads commands from stdin
            async def input_loop():
                loop = asyncio.get_event_loop()
                while True:
                    try:
                        raw = await loop.run_in_executor(
                            None,
                            lambda: input(f"\n[{state.role}] > ")
                        )
                    except (EOFError, KeyboardInterrupt):
                        console.print("[yellow]Interrupted. Goodbye![/yellow]")
                        await ws.close()
                        return

                    ws_msg, feedback = parse_command(raw, state)

                    if feedback:
                        console.print(feedback)

                    if ws_msg == 'QUIT':
                        await ws.close()
                        return

                    if ws_msg and isinstance(ws_msg, dict):
                        await ws.send(json.dumps(ws_msg))
                        if ws_msg.get('type') == 'submit_order':
                            state.has_submitted = True
                            state.add_log('order', f"Submitted order: {ws_msg['quantity']} units")

            # Run both concurrently
            await asyncio.gather(receiver(), input_loop())

    except websockets.exceptions.ConnectionRefusedError:
        console.print(f"[red]✗ Could not connect to {ws_url}[/red]")
        console.print("[dim]Make sure the Django server is running and Redis is available.[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        sys.exit(1)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='🍺 Beer Game CLI Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python client.py --token abc123xyz
  python client.py --host myserver.com --token abc123xyz
  python client.py --url ws://myserver.com:8000/ws/game/1/abc123xyz/
        """
    )
    parser.add_argument('--token',    help='Your player token (from the lobby invite link)')
    parser.add_argument('--host',     default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port',     default=8000, type=int, help='Server port (default: 8000)')
    parser.add_argument('--session',  default=1, type=int, help='Game session ID (default: 1)')
    parser.add_argument('--url',      help='Full WebSocket URL (overrides host/port/session/token)')
    parser.add_argument('--role',     default='unknown', help='Your role (for display only if auto-detected fails)')
    args = parser.parse_args()

    # Build WS URL
    if args.url:
        ws_url = args.url
        # Try to extract role from URL token later via server
        role = args.role
    elif args.token:
        ws_url = f"ws://{args.host}:{args.port}/ws/game/{args.session}/{args.token}/"
        role = args.role
    else:
        # Interactive setup
        console.print(Panel("[bold yellow]🍺 Beer Game CLI[/bold yellow]\nInteractive Setup", border_style="yellow"))
        console.print()
        console.print("You need your [cyan]invite token[/cyan] from the game lobby.")
        console.print("It looks like: [dim]ws://localhost:8000/ws/game/1/abc123.../[/dim]")
        console.print()

        host    = Prompt.ask("Server host", default="localhost")
        port    = IntPrompt.ask("Server port", default=8000)
        session = IntPrompt.ask("Session ID", default=1)
        token   = Prompt.ask("Your token")
        role    = Prompt.ask("Your role (for display)", choices=['retailer','wholesaler','distributor','factory'])
        ws_url  = f"ws://{host}:{port}/ws/game/{session}/{token}/"

    state = GameState(role)

    console.print(f"\n[dim]Connecting to:[/dim] [cyan]{ws_url}[/cyan]\n")
    console.print("[dim]Type [bold]help[/bold] for commands, [bold]order <n>[/bold] to submit your order.[/dim]\n")

    asyncio.run(run_client(ws_url, state))


if __name__ == '__main__':
    main()
