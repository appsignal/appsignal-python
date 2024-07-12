---
bump: patch
type: change
---

Rename heartbeats to cron check-ins. Calls to `appsignal.heartbeat` and `appsignal.Heartbeat` should be replaced with calls to `appsignal.check_in.cron` and `appsignal.check_in.Cron`, for example:

```python
# Before
from appsignal import heartbeat

def do_something():
  pass

heartbeat("do_something", do_something)

# After
from appsignal.check_in import cron

def do_something():
  pass

cron("do_something", do_something)
```
