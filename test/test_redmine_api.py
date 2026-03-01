import requests
import bootstrap


def test_repositories():
    endpoint = f"{bootstrap.REDMINE_URL_HTTPS}/repositories.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers, verify=False)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "projects" in data, f"Response missing 'projects' key: {data}"

    project = next((p for p in data["projects"] if p["name"] == bootstrap.PROJECT_NAME), None)
    assert project is not None, f"Project '{bootstrap.PROJECT_NAME}' not found in response"

    assert len(project["repositories"]) == 1
    repo = project["repositories"][0]
    assert repo["path"] == bootstrap.REPO_PATH
    assert repo["type"] == "Repository::Git"


def test_current_user():
    endpoint = f"{bootstrap.REDMINE_URL_HTTP}/users/current.json"
    headers = {"X-Redmine-API-Key": bootstrap.API_KEY}
    response = requests.get(endpoint, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert "user" in data
    assert "id" in data["user"]
