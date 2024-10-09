---
bump: patch
type: change
---

Send check-ins concurrently. When calling `appsignal.check_in.cron`, instead of blocking the current thread while the check-in events are sent, schedule them to be sent in a separate thread.
