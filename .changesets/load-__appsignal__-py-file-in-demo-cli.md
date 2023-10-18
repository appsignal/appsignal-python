---
bump: "patch"
type: "change"
---

When the `__appsignal__.py` file is found in the directory in which the demo CLI (`python -m appsignal demo`) is run, the AppSignal will now load the `__appsignal__.py`. When this configuration file is loaded, the demo CLI will use the configuration declared in that file to send the demo data to AppSignal. In this scenario, it will no longer prompt you to enter the application configuration manually.
