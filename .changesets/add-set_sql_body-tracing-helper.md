---
bump: "patch"
type: "add"
---

Add the `set_sql_body` tracing helper to set the body attribute on a span that contains a SQL query. When using this helper the given SQL query will be sanitized, reducing the chances of sending sensitive data to AppSignal.

```python
from appsignal import set_sql_body

# Must be used in an instrumented context -- e.g. a Django or Flask handler
def index():
    set_sql_body("SELECT * FROM users WHERE 'password' = 'secret'")
    # Will be stored as:
    set_sql_body("SELECT * FROM users WHERE 'password' = ?")
```

When the `set_body` helper is also used, the `set_sql_body` overwrites the `set_body` attribute.

More information about our [tracing helpers](https://docs.appsignal.com/python/instrumentation/instrumentation.html) can be found in our documentation.
