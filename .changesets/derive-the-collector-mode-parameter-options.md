---
bump: patch
type: change
---

In collector mode, the `filter_request_payload`, `filter_function_parameters` and `filter_request_query_parameters` configuration options now fall back to the value of `filter_parameters`, and the `send_request_payload`, `send_request_query_parameters` and `send_function_parameters` options fall back to the value of `send_params`. An application that filtered parameters or turned parameter reporting off keeps doing so after it switches to a collector, without having to set the new options.

Setting one of the new options still overrides the value that would be derived for it.
