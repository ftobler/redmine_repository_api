#!/usr/bin/env python3
"""Bootstrap a fresh Redmine instance for testing."""

import subprocess
import sys
import requests


API_KEY = "testAPIkeyTHROWAWAY123456"

REDMINE_URL_HTTP = "http://localhost"
REDMINE_URL_HTTPS = "https://localhost"

# Test projects and their repositories
PROJECTS = [
    {
        "name": "Project A",
        "identifier": "project-a",
        "repositories": [
            {"path": "/bogus/repo-a1", "type": "Repository::Git",        "identifier": "repo-a1"},
            {"path": "/bogus/repo-a2", "type": "Repository::Subversion", "identifier": "repo-a2"},
        ],
    },
    {
        "name": "Project B",
        "identifier": "project-b",
        "repositories": [
            {"path": "/bogus/repo-b1", "type": "Repository::Git", "identifier": "repo-b1"},
        ],
    },
    {
        "name": "Project C",
        "identifier": "project-c",
        "repositories": [],
    },
]

# Test users
API_USER_LOGIN = "api_user"
API_USER_KEY   = "apiUserTestKey789012"

NO_PERM_USER_LOGIN = "no_perm_user"
NO_PERM_USER_KEY   = "noPermUserTestKey789"


MYSQL = ["docker", "compose", "exec", "-T", "db", "mariadb",
         "-uredmine", "-predmine_password", "redmine"]


def sql(query):
    result = subprocess.run(MYSQL + ["-e", query], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {query[:60]}...")


def sql_val(query):
    """Run a query and return the first value of the first row."""
    result = subprocess.run(MYSQL + ["-se", query], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL query failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def inject_setting(key: str, value: str):
    sql(f"INSERT INTO settings (name, value, updated_on) VALUES ('{key}', '{value}', NOW()) ON DUPLICATE KEY UPDATE value = '{value}';")


def create_project(name: str, identifier: str) -> int:
    response = requests.post(
        f"{REDMINE_URL_HTTP}/projects.json",
        headers={"X-Redmine-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"project": {"name": name, "identifier": identifier, "is_public": True}},
    )
    if response.status_code != 201:
        print(f"Failed to create project '{name}': {response.text}", file=sys.stderr)
        sys.exit(1)
    project_id = response.json()["project"]["id"]
    print(f"OK: Created project '{name}' (id={project_id})")
    return project_id


def create_repository(project_id: int, path: str, repo_type: str, identifier: str, is_default: bool):
    sql(f"INSERT INTO repositories (project_id, url, type, identifier, is_default, created_on) "
        f"VALUES ({project_id}, '{path}', '{repo_type}', '{identifier}', {1 if is_default else 0}, NOW());")


def create_user(login: str, firstname: str, mail: str) -> int:
    response = requests.post(
        f"{REDMINE_URL_HTTP}/users.json",
        headers={"X-Redmine-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"user": {
            "login": login,
            "firstname": firstname,
            "lastname": "Test",
            "mail": mail,
            "password": "Password1!",
            "must_change_passwd": False,
            "status": 1,
        }},
    )
    if response.status_code != 201:
        print(f"Failed to create user '{login}': {response.text}", file=sys.stderr)
        sys.exit(1)
    user_id = response.json()["user"]["id"]
    print(f"OK: Created user '{login}' (id={user_id})")
    return user_id


def create_api_token(user_id: int, key: str):
    sql(f"INSERT INTO tokens (user_id, action, value, created_on, updated_on) VALUES ({user_id}, 'api', '{key}', NOW(), NOW());")


def create_role(name: str, permissions: list) -> int:
    # Redmine stores permissions as a YAML-serialised symbol array
    if permissions:
        yaml_perms = "---\\n" + "".join(f"- :{p}\\n" for p in permissions)
    else:
        yaml_perms = "--- []\\n"
    sql(f"INSERT INTO roles (name, permissions, issues_visibility, users_visibility, time_entries_visibility, assignable) "
        f"VALUES ('{name}', '{yaml_perms}', 'default', 'all', 'all', 1);")
    role_id = int(sql_val(f"SELECT id FROM roles WHERE name='{name}';"))
    print(f"OK: Created role '{name}' (id={role_id})")
    return role_id


def add_member(user_id: int, project_id: int, role_id: int):
    sql(f"INSERT INTO members (user_id, project_id, created_on, mail_notification) VALUES ({user_id}, {project_id}, NOW(), 0);")
    sql(f"INSERT INTO member_roles (member_id, role_id) SELECT id, {role_id} FROM members WHERE user_id={user_id} AND project_id={project_id};")


def inject_into_db():
    # admin user shall no longer change password on first login. it is kept with admin/admin.
    sql("UPDATE users SET must_change_passwd = 0 WHERE login = 'admin';")

    # enable REST api
    inject_setting("rest_api_enabled", "1")
    inject_setting("protocol", "https")
    inject_setting("host_name", "localhost")
    inject_setting("app_title", "Redmine Throwaway Test Instance")

    # inject a API token to be able to access the database
    # userid 1 is the admin, so this has access to everything.
    sql(f"INSERT INTO tokens (user_id, action, value, created_on, updated_on) VALUES (1, 'api', '{API_KEY}', NOW(), NOW());")

    # create test projects and repositories
    project_ids = {}
    for project in PROJECTS:
        project_id = create_project(project["name"], project["identifier"])
        project_ids[project["identifier"]] = project_id
        for i, repo in enumerate(project["repositories"]):
            create_repository(project_id, repo["path"], repo["type"], repo["identifier"], is_default=(i == 0))

    # create roles
    role_with_perm    = create_role("API User",   ["use_repository_api"])
    role_without_perm = create_role("Basic User", [])

    # create test users, assign tokens and project memberships
    api_user_id = create_user(API_USER_LOGIN, "Api", "api_user@example.com")
    create_api_token(api_user_id, API_USER_KEY)
    add_member(api_user_id, project_ids["project-a"], role_with_perm)

    no_perm_user_id = create_user(NO_PERM_USER_LOGIN, "Noperm", "no_perm_user@example.com")
    create_api_token(no_perm_user_id, NO_PERM_USER_KEY)
    add_member(no_perm_user_id, project_ids["project-b"], role_without_perm)

    print("Bootstrap complete.")


if __name__ == "__main__":
    inject_into_db()
