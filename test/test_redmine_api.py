import requests
import bootstrap


def get_projects():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers, verify=False)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "projects" in data, f"Response missing 'projects' key: {data}"
    return {p["name"]: p for p in data["projects"]}


def test_project_a_has_two_repos():
    projects = get_projects()
    assert "Project A" in projects, "Project A not found in response"
    repos = projects["Project A"]["repositories"]
    assert len(repos) == 2, f"Expected 2 repositories, got {len(repos)}"
    paths = {r["path"] for r in repos}
    assert "/bogus/repo-a1" in paths
    assert "/bogus/repo-a2" in paths
    types = {r["path"]: r["type"] for r in repos}
    assert types["/bogus/repo-a1"] == "Repository::Git"
    assert types["/bogus/repo-a2"] == "Repository::Subversion"


def test_project_b_has_one_repo():
    projects = get_projects()
    assert "Project B" in projects, "Project B not found in response"
    repos = projects["Project B"]["repositories"]
    assert len(repos) == 1, f"Expected 1 repository, got {len(repos)}"
    assert repos[0]["path"] == "/bogus/repo-b1"
    assert repos[0]["type"] == "Repository::Git"


def test_project_c_has_no_repos():
    projects = get_projects()
    assert "Project C" in projects, "Project C not found in response"
    repos = projects["Project C"]["repositories"]
    assert len(repos) == 0, f"Expected 0 repositories, got {len(repos)}"


def test_current_user():
    endpoint = f"{bootstrap.REDMINE_URL_HTTP}/users/current.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "user" in data
    assert "id" in data["user"]
