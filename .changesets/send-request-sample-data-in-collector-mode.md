---
bump: patch
type: fix
---

Emit request parameters and headers using the attribute names the collector
recognizes when in collector mode. `set_params` now emits
`appsignal.request.payload` instead of `appsignal.request.parameters`, and
`set_header` uses the `http.request.header` prefix instead of
`appsignal.request.headers`. The collector and server do not recognize the
previous names, so this sample data was previously dropped in collector mode.
