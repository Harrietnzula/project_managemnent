import tempfile
from pathlib import Path
import pytest
from models.user import User
from models.project import Project
from models.task import Task
from manager import DataManager
from utils.validators import validate_email, validate_date, validate_name


@pytest.fixture
def dm(tmp_path):
    manager = DataManager()
    manager._users = {}
    manager._projects = {}
    return manager


class TestUser:
    def test_creation(self):
        u = User("Alice", email="alice@co.io", role="admin")
        assert u.name == "Alice"
        assert u.role == "admin"
        assert u.projects == []

    def test_add_remove_project(self):
        u = User("Bob")
        u.add_project("Proj A")
        assert "Proj A" in u.projects
        u.add_project("Proj A")
        assert u.projects.count("Proj A") == 1
        u.remove_project("Proj A")
        assert "Proj A" not in u.projects

    def test_serialisation(self):
        u = User("Carol", email="carol@x.io", role="qa")
        u.add_project("Alpha")
        u2 = User.from_dict(u.to_dict())
        assert u2.name == u.name
        assert "Alpha" in u2.projects


class TestTask:
    def test_defaults(self):
        t = Task("Write tests")
        assert t.status == "todo"
        assert t.priority == "medium"

    def test_complete(self):
        t = Task("Deploy")
        t.complete()
        assert t.status == "done"
        assert t.completed_at != ""

    def test_invalid_status_falls_back(self):
        t = Task("Foo", status="nonexistent")
        assert t.status == "todo"

    def test_update_status(self):
        t = Task("Review PR")
        assert t.update_status("in-progress") is True
        assert t.update_status("flying") is False

    def test_serialisation(self):
        t = Task("Auth", priority="high", assignee="Dev")
        t.complete()
        t2 = Task.from_dict(t.to_dict())
        assert t2.title == "Auth"
        assert t2.status == "done"


class TestProject:
    def test_creation(self):
        p = Project("API", owner="Alice")
        assert p.title == "API"
        assert p.tasks == []

    def test_add_get_remove_task(self):
        p = Project("API", owner="Alice")
        t = Task("Setup DB")
        p.add_task(t)
        assert p.get_task("Setup DB") is t
        assert p.get_task("setup db") is t
        assert p.remove_task("Setup DB") is True
        assert p.get_task("Setup DB") is None

    def test_contributors(self):
        p = Project("X", owner="Alice")
        p.add_contributor("Bob")
        p.add_contributor("Bob")
        assert p.contributors == ["Bob"]


class TestDataManager:
    def test_add_and_get_user(self, dm):
        ok, _ = dm.add_user("Alice")
        assert ok is True
        assert dm.get_user("Alice") is not None

    def test_duplicate_user(self, dm):
        dm.add_user("Alice")
        ok, msg = dm.add_user("Alice")
        assert ok is False

    def test_delete_user(self, dm):
        dm.add_user("Bob")
        ok, _ = dm.delete_user("Bob")
        assert ok is True
        assert dm.get_user("Bob") is None

    def test_add_project_requires_user(self, dm):
        ok, msg = dm.add_project("My App", "Ghost")
        assert ok is False

    def test_add_project_success(self, dm):
        dm.add_user("Alice")
        ok, _ = dm.add_project("My App", "Alice")
        assert ok is True

    def test_add_task(self, dm):
        dm.add_user("Alice")
        dm.add_project("My App", "Alice")
        ok, _ = dm.add_task("My App", "Write tests")
        assert ok is True

    def test_complete_task(self, dm):
        dm.add_user("Alice")
        dm.add_project("My App", "Alice")
        dm.add_task("My App", "Deploy")
        ok, _ = dm.complete_task("My App", "Deploy")
        assert ok is True
        assert dm.get_project("My App").get_task("Deploy").status == "done"

    def test_search_projects(self, dm):
        dm.add_user("Alice")
        dm.add_project("Alpha API", "Alice", description="REST endpoints")
        dm.add_project("Beta Dashboard", "Alice")
        results = dm.search_projects("api")
        assert len(results) == 1

    def test_search_tasks(self, dm):
        dm.add_user("Alice")
        dm.add_project("My App", "Alice")
        dm.add_task("My App", "Write API docs")
        dm.add_task("My App", "Setup CI")
        results = dm.search_tasks("api")
        assert len(results) == 1


class TestValidators:
    def test_valid_email(self):
        assert validate_email("user@example.com") is True
        assert validate_email("bad-email") is False

    def test_valid_date(self):
        assert validate_date("2025-12-31") is True
        assert validate_date("31-12-2025") is False

    def test_valid_name(self):
        assert validate_name("Alice") is True
        assert validate_name("A") is False
        assert validate_name("") is False