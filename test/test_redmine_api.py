import requests
import bootstrap


def test_repositorys():
    url = bootstrap.REDMINE_URL_HTTPS
    api_key = bootstrap.API_KEY
    endpoint = f"{url}/repositories.json"

    headers = {"X-Redmine-API-Key": api_key}
    response = requests.get(endpoint, headers=headers, verify=False)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert "projects" in data, f"Response missing 'projects' key: {data}"


def test_current_user():
    url = bootstrap.REDMINE_URL_HTTP
    api_key = bootstrap.API_KEY
    endpoint = f"{url}/users/current.json"

    headers = {"X-Redmine-API-Key": api_key}
    print(headers, endpoint)

    response = requests.get(endpoint, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    print(data)
    assert "user" in data, "Response does not contain 'user'"
    assert "id" in data["user"], "User data missing 'id'"
