from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

console = Console()

STATUS_COLOUR = {
    "todo": "yellow",
    "in-progress": "cyan",
    "done": "green",
    "active": "green",
    "on-hold": "yellow",
    "completed": "bright_green",
    "archived": "dim",
}
PRIORITY_COLOUR = {"low": "dim", "medium": "blue", "high": "red"}


def success(msg):
    console.print(f"[bold green]✔[/bold green] {msg}")


def error(msg):
    console.print(f"[bold red]✘[/bold red] {msg}")


def info(msg):
    console.print(f"[bold cyan]ℹ[/bold cyan] {msg}")


def warn(msg):
    console.print(f"[bold yellow]⚠[/bold yellow] {msg}")


def print_users_table(users):
    if not users:
        warn("No users found.")
        return
    table = Table(title="Users", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Email")
    table.add_column("Role", style="italic")
    table.add_column("Projects", justify="right")
    table.add_column("Created")
    for i, u in enumerate(users, 1):
        table.add_row(
            str(i),
            u["name"],
            u.get("email", "—"),
            u.get("role", "developer"),
            str(len(u.get("projects", []))),
            u.get("created_at", "")[:10],
        )
    console.print(table)


def print_projects_table(projects):
    if not projects:
        warn("No projects found.")
        return
    table = Table(title="Projects", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Owner")
    table.add_column("Status")
    table.add_column("Tasks", justify="right")
    table.add_column("Progress")
    for i, p in enumerate(projects, 1):
        tasks = p.get("tasks", [])
        total = len(tasks)
        done = sum(1 for t in tasks if t.get("status") == "done")
        pct = f"{round(done/total*100)}%" if total else "—"
        status = p.get("status", "active")
        colour = STATUS_COLOUR.get(status, "white")
        table.add_row(
            str(i),
            p["title"],
            p.get("owner", "—"),
            f"[{colour}]{status}[/{colour}]",
            f"{done}/{total}",
            pct,
        )
    console.print(table)


def print_tasks_table(tasks, project_title=""):
    title = f"Tasks — {project_title}" if project_title else "Tasks"
    if not tasks:
        warn(f"No tasks in '{project_title}'.")
        return
    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_column("Assignee")
    table.add_column("Due")
    for i, t in enumerate(tasks, 1):
        status = t.get("status", "todo")
        priority = t.get("priority", "medium")
        s_col = STATUS_COLOUR.get(status, "white")
        p_col = PRIORITY_COLOUR.get(priority, "white")
        table.add_row(
            str(i),
            t["title"],
            f"[{s_col}]{status}[/{s_col}]",
            f"[{p_col}]{priority}[/{p_col}]",
            t.get("assignee", "—"),
            t.get("due_date", "—"),
        )
    console.print(table)


def print_project_detail(project):
    tasks = project.get("tasks", [])
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "done")
    pct = round(done / total * 100) if total else 0
    header = Text(project["title"], style="bold magenta")
    body = (
        f"Owner : {project.get('owner', '—')}\n"
        f"Status: {project.get('status', 'active')}\n"
        f"Desc  : {project.get('description', '—')}\n"
        f"Progress: {done}/{total} tasks done ({pct}%)\n"
        f"Contributors: {', '.join(project.get('contributors', [])) or '—'}"
    )
    console.print(Panel(body, title=header, expand=False))
    if tasks:
        print_tasks_table(tasks, project["title"])