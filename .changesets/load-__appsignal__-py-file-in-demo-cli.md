---
bump: "patch"
type: "change"
---

When the `__appsignal__.py` file is found in the directory in which the demo and diagnose CLIs are run (`python -m appsignal demo` or `python -m appsignal diagnose`), AppSignal will now load the `__appsignal__.py` file's configuration. When this file is loaded, the demo and diagnose CLI will use the configuration declared in that file to send the demo data and compile a diagnose report. In this scenario, it will no longer prompt you to enter the application configuration manually.
