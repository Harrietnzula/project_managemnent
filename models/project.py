from datetime import datetime
from models.task import Task


class Project:
    VALID_STATUSES = ("active", "on-hold", "completed", "archived")

    def __init__(self, title, owner, description="", status="active", contributors=None, created_at=None):
        self.title = title
        self.owner = owner
        self.description = description
        self.status = status if status in self.VALID_STATUSES else "active"
        self.contributors = contributors or []
        self.tasks = []
        self.created_at = created_at or datetime.now().isoformat()

    def add_task(self, task):
        self.tasks.append(task)

    def get_task(self, title):
        for task in self.tasks:
            if task.title.lower() == title.lower():
                return task
        return None

    def remove_task(self, title):
        task = self.get_task(title)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def add_contributor(self, username):
        if username not in self.contributors:
            self.contributors.append(username)

    def to_dict(self):
        return {
            "title": self.title,
            "owner": self.owner,
            "description": self.description,
            "status": self.status,
            "contributors": self.contributors,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        project = cls(
            title=data["title"],
            owner=data["owner"],
            description=data.get("description", ""),
            status=data.get("status", "active"),
            contributors=data.get("contributors", []),
            created_at=data.get("created_at"),
        )
        project.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return project