# End-to-End Testing

```bash
docker compose down
docker compose up -d

python test/wait_docker_ready.py

python test/bootstrap.py

.venv/bin/pytest test/ -v -s -W ignore::urllib3.exceptions.InsecureRequestWarning
```
