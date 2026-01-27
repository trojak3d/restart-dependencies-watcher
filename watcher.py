
import os
import time
import docker
from datetime import datetime, timezone

client = docker.from_env()

WATCH_CONTAINER = os.environ.get("WATCH_CONTAINER", "watch_container")
WATCH_LABEL = os.environ.get("WATCH_LABEL", "watcher.dependent")
POST_RESTART_DELAY = int(os.environ.get("POST_RESTART_DELAY", "10"))
COOLDOWN = int(os.environ.get("COOLDOWN", "30"))

last_restart_time = None

def log(msg):
    print(msg, flush=True)

def get_dependent_containers():
    key, value = WATCH_LABEL.split(":")
    return client.containers.list(
        all=True,
        filters={"label": f"{key.strip()}={value.strip()}"}
    )

def restart_containers(containers):
    global last_restart_time

    now = datetime.now(timezone.utc)
    if last_restart_time:
        elapsed = (now - last_restart_time).total_seconds()
        if elapsed < COOLDOWN:
            wait_time = COOLDOWN - elapsed
            log(f"Cooldown active ({elapsed:.0f}s elapsed). Waiting {wait_time:.0f}s...")
            time.sleep(wait_time)

    log(f"{WATCH_CONTAINER} restarted. Will restart all containers matching {WATCH_LABEL}")
    time.sleep(POST_RESTART_DELAY)

    for c in containers:
        try:
            c.restart()
            log(f"{c.name} successfully started")
        except Exception as e:
            log(f"{c.name} error restarting: {e}")

    last_restart_time = datetime.now(timezone.utc)
    log("Finished restarting containers")

def main():
    log("Restart watcher started:")
    log(f" - Watch Container: {WATCH_CONTAINER}")
    log(f" - Watch Label: {WATCH_LABEL}")
    log(f" - Post Restart Delay: {POST_RESTART_DELAY}s")
    log(f" - Cooldown: {COOLDOWN}s")
    log(" - Watched containers:")
    for c in get_dependent_containers():
        log(f"   - {c.name}")

    # Listen to events
    for event in client.events(decode=True):
        if (
            event.get("Type") == "container" and
            event.get("Actor", {}).get("Attributes", {}).get("name") == WATCH_CONTAINER and
            event.get("Action") in ["restart", "die", "health_status: unhealthy"]
        ):
            restart_containers(get_dependent_containers())

if __name__ == "__main__":
    main()
