---
bump: "patch"
type: "add"
---

Add the `--environment` CLI option to the demo CLI tool. This allow you to configure to which app environment the demo samples should be sent. It would default to production (and only be configurable via the `APPSIGNAL_APP_ENV` environment variable), but now it's configurable through the CLI options as well.

```
python -m appsignal demo --environment=production
```
