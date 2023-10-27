---
bump: "patch"
type: "fix"
---

Fix the diagnose report CLI exiting with an error when a path was not found. When a file, like the `appsignal.log` file, was not found, the diagnose CLI would exit with an error when trying to read from the file. It will now no longer try to read a non-existing file and no longer error.
