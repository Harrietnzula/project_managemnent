import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filename):
    ensure_dir()
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


def save_json(data, filename):
    ensure_dir()
    filepath = DATA_DIR / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_users():
    return load_json("users.json")


def save_users(data):
    save_json(data, "users.json")


def load_projects():
    return load_json("projects.json")


def save_projects(data):
    save_json(data, "projects.json")