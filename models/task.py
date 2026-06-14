from datetime import datetime


class Task:
    VALID_STATUSES = ("todo", "in-progress", "done")
    VALID_PRIORITIES = ("low", "medium", "high")

    def __init__(self, title, description="", status="todo", priority="medium", assignee="", due_date="", created_at=None):
        self.title = title
        self.description = description
        self.status = status if status in self.VALID_STATUSES else "todo"
        self.priority = priority if priority in self.VALID_PRIORITIES else "medium"
        self.assignee = assignee
        self.due_date = due_date
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = ""

    def complete(self):
        self.status = "done"
        self.completed_at = datetime.now().isoformat()

    def update_status(self, status):
        if status in self.VALID_STATUSES:
            self.status = status
            if status == "done" and not self.completed_at:
                self.completed_at = datetime.now().isoformat()
            return True
        return False

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "todo"),
            priority=data.get("priority", "medium"),
            assignee=data.get("assignee", ""),
            due_date=data.get("due_date", ""),
            created_at=data.get("created_at"),
        )
        task.completed_at = data.get("completed_at", "")
        return task