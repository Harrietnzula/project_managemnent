from datetime import datetime


class User:
    def __init__(self, name, email="", role="developer", created_at=None):
        self.name = name
        self.email = email
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.projects = []

    def add_project(self, project_title):
        if project_title not in self.projects:
            self.projects.append(project_title)

    def remove_project(self, project_title):
        if project_title in self.projects:
            self.projects.remove(project_title)

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "projects": self.projects,
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            name=data["name"],
            email=data.get("email", ""),
            role=data.get("role", "developer"),
            created_at=data.get("created_at"),
        )
        user.projects = data.get("projects", [])
        return user