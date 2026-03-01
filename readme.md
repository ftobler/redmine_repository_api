# Redmine Repository API Plugin

[![Integration Tests](https://github.com/ftobler/redmine_repository_api/actions/workflows/check.yml/badge.svg)](https://github.com/ftobler/redmine_repository_api/actions/workflows/check.yml)

Exposes a REST API endpoint listing all projects and their repositories that the authenticated user has permission to view.

## API

### `GET /repositories.json`

Returns all accessible projects and their repositories. **May include server internal path**

**Authentication:**  
Redmine API key via header or query param. REST API must be enabled.

**Permission:**  
The calling user must have the `use_repository_api` permission.

**example call:**  
`curl -H "X-Redmine-API-Key: <your_api_key>" https://<redmine>/repositories.json?type=git`

**Query parameters:**

| Parameter   | Description                                               | Example                         |
|-------------|-----------------------------------------------------------|---------------------------------|
| `type`      | Filter repositories by SCM type (case-insensitive)        | `?type=git`, `?type=subversion` |
| `non_empty` | Omit projects with no repositories (after type filtering) | `?non_empty=1`                  |

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "My Project",
      "repositories": [
        {
          "id": 1,
          "name": "Main repository",
          "type": "Repository::Git",
          "path": "/path/to/repo"
        }
      ]
    }
  ]
}
```

## Development & Testing

Spin up a throwaway Redmine instance and initialize it:

```
docker compose up
python test/bootstrap.py
```

Then run the test suite:

```
pytest test/
```

Customize API keys and OAuth settings in `test/bootstrap.py`.

## Installation

Need Redmine 5 or higher.

1. Copy the plugin into `plugins/redmine_repository_api`
2. Run:
   bundle install
   bin/rails redmine:plugins:migrate RAILS_ENV=production
3. Restart Redmine