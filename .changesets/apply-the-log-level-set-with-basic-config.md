---
bump: patch
type: fix
---

`logging.basicConfig()` applies the log level it is given. An application that calls it with a level below `WARNING`, such as `logging.INFO`, starts sending its log lines at that level.
