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


def test_filter_by_type_git():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers, params={"type": "git"}, verify=False)
    assert response.status_code == 200

    projects = {p["name"]: p for p in response.json()["projects"]}

    # Project A: only the git repo survives, svn is filtered out
    assert len(projects["Project A"]["repositories"]) == 1
    assert projects["Project A"]["repositories"][0]["path"] == "/bogus/repo-a1"

    # Project B: git repo still present
    assert len(projects["Project B"]["repositories"]) == 1

    # Project C: still present, just empty
    assert "Project C" in projects
    assert len(projects["Project C"]["repositories"]) == 0

    # No svn repos anywhere
    for p in projects.values():
        for r in p["repositories"]:
            assert r["type"] == "Repository::Git"


def test_filter_by_type_subversion():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers, params={"type": "subversion"}, verify=False)
    assert response.status_code == 200

    projects = {p["name"]: p for p in response.json()["projects"]}

    # Project A: only the svn repo survives
    assert len(projects["Project A"]["repositories"]) == 1
    assert projects["Project A"]["repositories"][0]["path"] == "/bogus/repo-a2"

    # Project B and C: no svn repos
    assert len(projects["Project B"]["repositories"]) == 0
    assert len(projects["Project C"]["repositories"]) == 0


def test_filter_non_empty():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers, params={"non_empty": "1"}, verify=False)
    assert response.status_code == 200

    projects = {p["name"]: p for p in response.json()["projects"]}

    assert "Project A" in projects
    assert "Project B" in projects
    assert "Project C" not in projects, "Project C has no repos and should be excluded"


def test_filter_by_type_and_non_empty():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers, params={"type": "subversion", "non_empty": "1"}, verify=False)
    assert response.status_code == 200

    projects = {p["name"]: p for p in response.json()["projects"]}

    # Only Project A has a subversion repo
    assert "Project A" in projects
    assert len(projects["Project A"]["repositories"]) == 1
    assert "Project B" not in projects
    assert "Project C" not in projects


def test_current_user():
    endpoint = f"{bootstrap.REDMINE_URL_HTTP}/users/current.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "user" in data
    assert "id" in data["user"]


def test_user_with_permission():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_USER_KEY}
    response = requests.get(endpoint, headers=headers, verify=False)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


def test_user_without_permission():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.NO_PERM_USER_KEY}
    response = requests.get(endpoint, headers=headers, verify=False)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"


def test_no_api_key():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    response = requests.get(endpoint, verify=False)
    assert response.status_code == 401


def test_wrong_api_key():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": "wrong-key"}
    response = requests.get(endpoint, headers=headers, verify=False)
    assert response.status_code == 401
