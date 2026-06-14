import argparse
import sys
from manager import DataManager
from utils.display import console, success, error, info, warn, print_users_table, print_projects_table, print_tasks_table, print_project_detail
from utils.validators import validate_email, validate_date, validate_name

dm = DataManager()


def cmd_add_user(args):
    if not validate_name(args.name):
        error("Name must be at least 2 characters.")
        sys.exit(1)
    if args.email and not validate_email(args.email):
        error(f"'{args.email}' is not a valid email.")
        sys.exit(1)
    ok, msg = dm.add_user(args.name, email=args.email or "", role=args.role)
    (success if ok else error)(msg)


def cmd_list_users(args):
    print_users_table([u.to_dict() for u in dm.list_users()])


def cmd_delete_user(args):
    ok, msg = dm.delete_user(args.name)
    (success if ok else error)(msg)


def cmd_add_project(args):
    ok, msg = dm.add_project(args.title, args.user, description=args.desc or "")
    (success if ok else error)(msg)


def cmd_list_projects(args):
    print_projects_table([p.to_dict() for p in dm.list_projects(owner=args.user)])


def cmd_show_project(args):
    project = dm.get_project(args.title)
    if not project:
        error(f"Project '{args.title}' not found.")
        sys.exit(1)
    print_project_detail(project.to_dict())


def cmd_update_project(args):
    ok, msg = dm.update_project_status(args.title, args.status)
    (success if ok else error)(msg)


def cmd_delete_project(args):
    ok, msg = dm.delete_project(args.title)
    (success if ok else error)(msg)


def cmd_add_contributor(args):
    ok, msg = dm.add_contributor(args.project, args.user)
    (success if ok else error)(msg)


def cmd_add_task(args):
    if args.due and not validate_date(args.due):
        error("Due date must be YYYY-MM-DD format.")
        sys.exit(1)
    ok, msg = dm.add_task(args.project, args.title, description=args.desc or "", priority=args.priority, assignee=args.assignee or "", due_date=args.due or "")
    (success if ok else error)(msg)


def cmd_list_tasks(args):
    project = dm.get_project(args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        sys.exit(1)
    print_tasks_table([t.to_dict() for t in project.tasks], args.project)


def cmd_complete_task(args):
    ok, msg = dm.complete_task(args.project, args.task)
    (success if ok else error)(msg)


def cmd_update_task(args):
    ok, msg = dm.update_task_status(args.project, args.task, args.status)
    (success if ok else error)(msg)


def cmd_delete_task(args):
    ok, msg = dm.delete_task(args.project, args.task)
    (success if ok else error)(msg)


def cmd_search(args):
    projects = dm.search_projects(args.query)
    task_hits = dm.search_tasks(args.query)
    if projects:
        info(f"Projects matching '{args.query}':")
        print_projects_table([p.to_dict() for p in projects])
    else:
        warn(f"No projects match '{args.query}'.")
    if task_hits:
        info(f"Tasks matching '{args.query}':")
        for proj, task in task_hits:
            console.print(f"  [dim]{proj.title}[/dim] → [bold]{task.title}[/bold] [{task.status}]")
    else:
        warn(f"No tasks match '{args.query}'.")


def build_parser():
    parser = argparse.ArgumentParser(prog="pm", description="Project Management CLI")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # Users
    p = sub.add_parser("add-user", help="Create a new user")
    p.add_argument("--name", required=True)
    p.add_argument("--email", default="")
    p.add_argument("--role", default="developer", choices=["developer", "designer", "manager", "qa", "admin"])
    p.set_defaults(func=cmd_add_user)

    p = sub.add_parser("list-users", help="List all users")
    p.set_defaults(func=cmd_list_users)

    p = sub.add_parser("delete-user", help="Delete a user")
    p.add_argument("--name", required=True)
    p.set_defaults(func=cmd_delete_user)

    # Projects
    p = sub.add_parser("add-project", help="Create a project")
    p.add_argument("--user", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--desc", default="")
    p.set_defaults(func=cmd_add_project)

    p = sub.add_parser("list-projects", help="List all projects")
    p.add_argument("--user", default=None)
    p.set_defaults(func=cmd_list_projects)

    p = sub.add_parser("show-project", help="Show project details")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_show_project)

    p = sub.add_parser("update-project", help="Update project status")
    p.add_argument("--title", required=True)
    p.add_argument("--status", required=True, choices=["active", "on-hold", "completed", "archived"])
    p.set_defaults(func=cmd_update_project)

    p = sub.add_parser("delete-project", help="Delete a project")
    p.add_argument("--title", required=True)
    p.set_defaults(func=cmd_delete_project)

    p = sub.add_parser("add-contributor", help="Add contributor to project")
    p.add_argument("--project", required=True)
    p.add_argument("--user", required=True)
    p.set_defaults(func=cmd_add_contributor)

    # Tasks
    p = sub.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--priority", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--assignee", default="")
    p.add_argument("--due", default="")
    p.set_defaults(func=cmd_add_task)

    p = sub.add_parser("list-tasks", help="List tasks in a project")
    p.add_argument("--project", required=True)
    p.set_defaults(func=cmd_list_tasks)

    p = sub.add_parser("complete-task", help="Mark a task as done")
    p.add_argument("--project", required=True)
    p.add_argument("--task", required=True)
    p.set_defaults(func=cmd_complete_task)

    p = sub.add_parser("update-task", help="Update task status")
    p.add_argument("--project", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--status", required=True, choices=["todo", "in-progress", "done"])
    p.set_defaults(func=cmd_update_task)

    p = sub.add_parser("delete-task", help="Delete a task")
    p.add_argument("--project", required=True)
    p.add_argument("--task", required=True)
    p.set_defaults(func=cmd_delete_task)

    # Search
    p = sub.add_parser("search", help="Search projects and tasks")
    p.add_argument("--query", required=True)
    p.set_defaults(func=cmd_search)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main() 
