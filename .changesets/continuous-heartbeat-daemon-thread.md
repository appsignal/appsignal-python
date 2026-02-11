---
bump: patch
type: fix
---

Fix an issue where usage of continuous heartbeats would stop an application from winding down unless `appsignal.stop()` was called.