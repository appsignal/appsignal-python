---
bump: "patch"
type: "fix"
---

Fix the metadata on the demo CLI's example samples. It will no longer contain unused attributes. The performance sample will report a named `process_request.http` event, rather than report an `unknown` event, in the event timeline.
