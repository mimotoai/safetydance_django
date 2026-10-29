from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("safetydance-django")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
