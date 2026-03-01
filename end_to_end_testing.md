# End-to-End Testing

```bash
docker compose down
docker compose up -d

# Wait for Redmine to be ready
for i in $(seq 1 36); do curl -sf http://localhost/ > /dev/null && echo "Redmine is up!" && break; echo "Attempt $i/36..."; sleep 5; done

python test/bootstrap.py

.venv/bin/pytest test/ -v -s -W ignore::urllib3.exceptions.InsecureRequestWarning
```
