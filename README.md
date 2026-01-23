
# restart-dependencies-watcher

[![GitHub Repo](https://img.shields.io/badge/GitHub-trojak3d/restart--dependencies--watcher-blue?logo=github)](https://github.com/trojak3d/restart-dependencies-watcher)  
[![Docker Hub](https://img.shields.io/badge/DockerHub-trojak3d%2Frestart--dependencies--watcher-blue?logo=docker)](https://hub.docker.com/repository/docker/trojak3d/restart-dependencies-watcher)

A lightweight, event-driven Docker helper container that monitors a specific container for restart events and automatically restarts dependent containers marked with a specific label. Useful for coordinating service restarts inside any Docker environment.

## How it works

1. On startup, the watcher:
   - Reads configuration from environment variables
   - Lists containers matching the dependency label
   - Connects to the Docker Engine event stream

2. When the watched container restarts, the watcher:
   - Waits `POST_RESTART_DELAY` seconds
   - Applies a `COOLDOWN` window to avoid rapid restart loops
   - Restarts all containers that match `WATCH_LABEL`
   - Logs the outcome of each restart

The watcher then continues listening for future events.

## Requirements

- Docker Engine
- Access to the Docker socket:
  - `/var/run/docker.sock` (recommended read-only)

> **Security note:** Mounting the Docker socket gives the container broad control over your host. Use only in trusted environments.

## Configuration

Environment variables:

- `WATCH_CONTAINER` – Name of the container to monitor
- `WATCH_LABEL` – Label key/value used to find dependent containers
- `POST_RESTART_DELAY` – Seconds to wait after a restart event
- `COOLDOWN` – Minimum seconds between restart cycles

## Example Docker Compose Configuration

```yaml
depends-watcher:
  image: trojak3d/restart-dependencies-watcher:latest
  container_name: restart-dependencies-watcher
  environment:
    WATCH_CONTAINER: "service-to-watch"
    WATCH_LABEL: "dependent.service: true"
    POST_RESTART_DELAY: "10"
    COOLDOWN: "30"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  restart: unless-stopped
```

## Marking Dependent Containers

Add the configured label to any container that should be restarted.

```yaml
labels:
  dependent.service: "true"
```

## Logging

Example output:

```
Restart watcher started:
 - Watch Container: service-to-watch
 - Watch Label: dependent.service: true
 - Post Restart Delay: 10s
 - Cooldown: 30s
 - Watched containers:
   - app1
   - app2

service-to-watch restarted. Will restart all containers matching dependent.service: true
app1 successfully started
app2 successfully started
Finished restarting containers
```

## License

MIT License