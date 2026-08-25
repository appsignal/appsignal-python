---
bump: patch
type: fix
---

Report `unknown` as the host name in collector mode when the `hostname`
configuration option is set to `None`. Apps that set it that way reported no
host name at all.
