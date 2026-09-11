---
bump: patch
type: change
---

The `filter_parameters` and `send_params` configuration options are deprecated in collector mode. Use `filter_request_payload`, `filter_function_parameters` and `filter_request_query_parameters` to filter different kinds of parameters, and `send_request_payload`, `send_request_query_parameters` and `send_function_parameters` to choose which kinds of parameters to report.

AppSignal warns about the deprecated options at startup, and names the value to set for each option that replaces them.

In agent mode, `filter_parameters` and `send_params` still apply to every kind of parameter, and the new options have no effect.
