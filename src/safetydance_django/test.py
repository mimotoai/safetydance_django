"""The one-line import for test modules: ``from safetydance_django.test import *``.

Importing this module registers the ``http`` steps and brings in the
safetydance prefixes, ``test_context`` and the ``Http`` context data.
"""
from safetydance import And, Given, Then, When, test_context

from .steps import Http  # importing the module registers the steps

__all__ = ["And", "Given", "Http", "Then", "When", "test_context"]
