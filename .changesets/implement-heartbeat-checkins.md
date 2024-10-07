---
bump: minor
type: add
---

Add support for heartbeat check-ins.

Use the `appsignal.check_in.heartbeat` function to send a single heartbeat check-in event from your application. This can be used, for example, in your application's main loop:

```python
from appsignal.check_in import heartbeat

while True:
  heartbeat("job_processor")
  process_job()
```

Heartbeats are deduplicated and sent asynchronously, without blocking the current thread. Regardless of how often the `.heartbeat` function is called, at most one heartbeat with the same identifier will be sent every ten seconds.

Pass `continuous=True` as the second argument to send heartbeats continuously during the entire lifetime of the current process. This can be used, for example, after your application has finished its boot process:

```python
def main():
  start_app()
  heartbeat("my_app", continuous=True)
```
