---
bump: "patch"
type: "add"
---

Add sample data helpers. These helpers simplify adding properties to OpenTelemetry spans that display specific data in the AppSignal sample UI. For example, to add custom data to the current sample:

```python
from appsignal import set_custom_data

# Must be used in an instrumented context -- e.g. a Flask handler
@app.get("/")
def index():
  set_custom_data({"hello": "there"})
```

The full list of sample data helpers is available in our documentation as part of the [tagging and sample data guides](https://docs.appsignal.com/guides/custom-data.html) and [namespace guide](https://docs.appsignal.com/guides/namespaces.html).
