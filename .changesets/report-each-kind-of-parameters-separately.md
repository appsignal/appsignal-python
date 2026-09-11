---
bump: patch
type: change
---

In collector mode, the Django and Flask instrumentation now reports a request's query string as query parameters rather than as a request payload. So `filter_request_query_parameters` and `send_request_query_parameters` apply to a query string, and `filter_request_payload` and `send_request_payload` apply to a Django request's body.

In agent mode, a Flask application's query parameters are now reported on their own, rather than nested under an `args` key. Django reports what it reported before.
