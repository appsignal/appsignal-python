---
bump: "patch"
type: "change"
---

Change the configuration source load order. The environment variables are no longer leading, but the `__appsignal__.py` file source is. The load order is now:

- Default source (hardcoded config)
- System source (context dependent config)
- Environment source (environment variables)
- Initial source (any config given to `Config()` in `__appsignal__.py`)
