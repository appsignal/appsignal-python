---
bump: "patch"
type: "add"
---

Add error helpers. These helpers simplify reporting errors to AppSignal that are not handled automatically by your framework, alongside the current instrumented context or separately. For example, to report an error from an `except` clause as a separate sample:

```python
from appsignal import send_error

def index():
  cookies = put_hand_in_cookie_jar()
  except HandStuckError as error:
    send_error(error)
```

More information about [error helpers](https://docs.appsignal.com/python/custom-instrumentation/exception-handling.html) is available in our documentation.
