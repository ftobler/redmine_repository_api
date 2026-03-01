# Redmine Repository API Plugin

Exposes a REST API endpoint listing all projects and their repositories that the authenticated user has permission to view.

## API

### `GET /repositories.json`

Returns all accessible projects and their repositories.

**Authentication:** Redmine API key via header or query param. REST API must be enabled in *Administration > Settings > API*.

```
curl -H "X-Redmine-API-Key: <your_api_key>" https://<redmine>/repositories.json
```

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