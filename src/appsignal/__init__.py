from .client import Client as Appsignal


__all__ = ["Appsignal"]

# Try and load the appsignal-beta package. If it's present and imported, it
# will print a message about switching to the `appsignal` package.
try:
    import appsignal_beta  # type:ignore # noqa: F401
except ImportError:
    pass
