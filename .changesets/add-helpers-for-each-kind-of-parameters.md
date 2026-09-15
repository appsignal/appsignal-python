---
bump: minor
type: add
---

Add the `set_request_payload`, `set_request_query_parameters` and `set_function_parameters` helpers. Each one reports a kind of parameters that collector mode keeps apart, so the option that filters that kind, and the one that suppresses it, apply to what you report:

```python
from appsignal import set_function_parameters

set_function_parameters({"user_id": 123})
```

The `set_params` helper reports the request payload, which is what it has always reported.

In agent mode there is one place to report parameters, so all four helpers report to it and the last one called is the one that takes effect.
