from models.user import User
from models.project import Project
from models.task import Task
from utils.storage import load_users, save_users, load_projects, save_projects


class DataManager:
    def __init__(self):
        self._users = {}
        self._projects = {}
        self.load()

    def load(self):
        raw_users = load_users()
        self._users = {k: User.from_dict(v) for k, v in raw_users.items()}
        raw_projects = load_projects()
        self._projects = {k: Project.from_dict(v) for k, v in raw_projects.items()}

    def save(self):
        save_users({k: v.to_dict() for k, v in self._users.items()})
        save_projects({k: v.to_dict() for k, v in self._projects.items()})

    # Users
    def add_user(self, name, email="", role="developer"):
        if name in self._users:
            return False, f"User '{name}' already exists."
        self._users[name] = User(name=name, email=email, role=role)
        self.save()
        return True, f"User '{name}' created."

    def get_user(self, name):
        return self._users.get(name)

    def list_users(self):
        return list(self._users.values())

    def delete_user(self, name):
        if name not in self._users:
            return False, f"User '{name}' not found."
        del self._users[name]
        self.save()
        return True, f"User '{name}' deleted."

    # Projects
    def add_project(self, title, owner, description=""):
        if title in self._projects:
            return False, f"Project '{title}' already exists."
        if owner not in self._users:
            return False, f"User '{owner}' not found."
        self._projects[title] = Project(title=title, owner=owner, description=description)
        self._users[owner].add_project(title)
        self.save()
        return True, f"Project '{title}' created for '{owner}'."

    def get_project(self, title):
        return self._projects.get(title)

    def list_projects(self, owner=None):
        projects = list(self._projects.values())
        if owner:
            projects = [p for p in projects if p.owner == owner]
        return projects

    def update_project_status(self, title, status):
        project = self.get_project(title)
        if not project:
            return False, f"Project '{title}' not found."
        if status not in Project.VALID_STATUSES:
            return False, f"Invalid status. Choose from: {', '.join(Project.VALID_STATUSES)}"
        project.status = status
        self.save()
        return True, f"Project '{title}' status set to '{status}'."

    def add_contributor(self, project_title, username):
        project = self.get_project(project_title)
        if not project:
            return False, f"Project '{project_title}' not found."
        if username not in self._users:
            return False, f"User '{username}' not found."
        project.add_contributor(username)
        self._users[username].add_project(project_title)
        self.save()
        return True, f"'{username}' added as contributor to '{project_title}'."

    def delete_project(self, title):
        if title not in self._projects:
            return False, f"Project '{title}' not found."
        del self._projects[title]
        for user in self._users.values():
            user.remove_project(title)
        self.save()
        return True, f"Project '{title}' deleted."

    # Tasks
    def add_task(self, project_title, title, description="", priority="medium", assignee="", due_date=""):
        project = self.get_project(project_title)
        if not project:
            return False, f"Project '{project_title}' not found."
        if project.get_task(title):
            return False, f"Task '{title}' already exists."
        project.add_task(Task(title=title, description=description, priority=priority, assignee=assignee, due_date=due_date))
        self.save()
        return True, f"Task '{title}' added to '{project_title}'."

    def complete_task(self, project_title, task_title):
        project = self.get_project(project_title)
        if not project:
            return False, f"Project '{project_title}' not found."
        task = project.get_task(task_title)
        if not task:
            return False, f"Task '{task_title}' not found."
        task.complete()
        self.save()
        return True, f"Task '{task_title}' marked as done."

    def update_task_status(self, project_title, task_title, status):
        project = self.get_project(project_title)
        if not project:
            return False, f"Project '{project_title}' not found."
        task = project.get_task(task_title)
        if not task:
            return False, f"Task '{task_title}' not found."
        if not task.update_status(status):
            return False, f"Invalid status '{status}'."
        self.save()
        return True, f"Task '{task_title}' status updated to '{status}'."

    def delete_task(self, project_title, task_title):
        project = self.get_project(project_title)
        if not project:
            return False, f"Project '{project_title}' not found."
        if not project.remove_task(task_title):
            return False, f"Task '{task_title}' not found."
        self.save()
        return True, f"Task '{task_title}' removed."

    # Search
    def search_projects(self, query):
        q = query.lower()
        return [p for p in self._projects.values() if q in p.title.lower() or q in p.description.lower()]

    def search_tasks(self, query):
        q = query.lower()
        results = []
        for project in self._projects.values():
            for task in project.tasks:
                if q in task.title.lower() or q in task.description.lower():
                    results.append((project, task))
        return results 
