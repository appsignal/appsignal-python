---
bump: patch
type: fix
---

An option set to `None` when initializing the `Appsignal` client no longer replaces a value that AppSignal detected itself. For example, `Appsignal(hostname=None)` now reports the detected hostname, instead of reporting no hostname at all. Options that AppSignal does not detect are unchanged: setting `request_headers` to `None`, for example, still turns off request header collection.
