---
bump: minor
type: add
---

Add an `is_active` attribute to the AppSignal client. It tells you whether AppSignal is configured to start, so you can use it to only run code that makes sense when AppSignal is active:

```python
from appsignal import Appsignal

appsignal = Appsignal(name="My app name", push_api_key="my-push-api-key", active=True)

if appsignal.is_active:
    # Only runs when AppSignal is active
```

Before this change, the only way to check this was to read the client's private configuration object.
