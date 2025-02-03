---
bump: patch
type: fix
---

Fix an issue where calling `appsignal.stop()` after sending check-in events would leave a dangling thread, stopping the application from shutting down correctly.
