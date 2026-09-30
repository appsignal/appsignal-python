---
bump: patch
type: fix
---

Fix an issue where AppSignal would configure redundant handlers when starting again in a forked process, such as when a Celery worker calls `appsignal.start()` from the `worker_process_init` signal.