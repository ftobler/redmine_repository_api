# Redmine Repository API Plugin

Exposes a REST API endpoint listing all projects and their repositories that the authenticated user has permission to view.

## API

### `GET /repositories.json`

Returns all accessible projects and their repositories.

**Authentication:** Redmine API key via header or query param. REST API must be enabled.

**Permission:** The calling user must have the `use_repository_api` permission.

```
curl -H "X-Redmine-API-Key: <your_api_key>" https://<redmine>/repositories.json
```

**Query parameters:**

| Parameter   | Description                                               | Example                         |
|-------------|-----------------------------------------------------------|---------------------------------|
| `type`      | Filter repositories by SCM type (case-insensitive)        | `?type=git`, `?type=subversion` |
| `non_empty` | Omit projects with no repositories (after type filtering) | `?non_empty=1`                  |

Parameters can be combined: `?type=git&non_empty=1`

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

1. Copy the plugin into `plugins/redmine_repository_api`
2. Run:
   bundle install
   bin/rails redmine:plugins:migrate RAILS_ENV=production
3. Restart Redmine