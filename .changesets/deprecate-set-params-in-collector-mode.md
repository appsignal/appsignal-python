---
bump: patch
type: change
---

The `set_params` helper is deprecated when a collector is used. It does not say which kind of parameters it is given, so everything it reports becomes the request payload. Use `set_request_payload`, `set_request_query_parameters` or `set_function_parameters` instead, so that the options which filter that kind of parameters, and the ones which suppress it, apply to what you report.

AppSignal warns the first time the helper is used. In agent mode there is one place to report parameters, so the helper is not deprecated there.
