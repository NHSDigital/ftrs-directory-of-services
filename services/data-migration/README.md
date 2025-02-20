# Data Migration Pipeline

## Start Database Container

For local development, this project relies on a local Postgres instance running in a docker container.
This container will persist data at `./.tmp/pg_data/`.

```bash
podman compose up -d
```
