---
bump: "patch"
type: "fix"
---

Fix the agent diagnostic report in diagnose CLI tool (`python -m appsignal diagnose`). The agent diagnose report would always contain an error, because it did not pick up the AppSignal configuration properly. There's still an issue that it does not read from the `__appsignal__.py` configuration file, which will be addressed later.
