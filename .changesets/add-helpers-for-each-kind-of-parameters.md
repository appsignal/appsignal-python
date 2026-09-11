---
bump: minor
type: add
---

Add the `set_request_payload`, `set_request_query_parameters` and `set_function_parameters` helpers. Each one reports a kind of parameters that collector mode keeps apart, so the option that filters that kind, and the one that suppresses it, apply to what you report:

```python
from appsignal import set_function_parameters

set_function_parameters({"user_id": 123})
```

In collector mode, the `set_params` helper is now deprecated, and it reports the request payload. It does not say which kind of parameters it is given, so use `set_request_payload`, `set_request_query_parameters` or `set_function_parameters` instead. AppSignal warns the first time it is used.

In agent mode there is one place to report parameters, so all four helpers report to it, the last one called is the one that takes effect, and `set_params` is not deprecated.
