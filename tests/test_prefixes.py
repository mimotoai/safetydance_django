import subprocess
import sys

from django.urls import reverse
import pytest
from safetydance_django.test import *

SCRIPT = """
import sys, django
from django.conf import settings
settings.configure(INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "rest_framework"])
django.setup()
from safetydance import Given
assert "safetydance_django.steps" not in sys.modules
Given.http.get
assert "safetydance_django.steps" in sys.modules
"""


@pytest.mark.django_db
@test_context
def test_get():
    Given.http.get(reverse("simple-list"))
    Then.http.status_code_is(200)


@pytest.mark.django_db
@test_context
def test_full_module_path():
    When.safetydance_django.steps.get(reverse("simple-list"))
    And.http.status_code_is(200)


@pytest.mark.django_db
@test_context
def test_prefix_steps_share_the_context():
    Given.http.get(reverse("simple-list"))
    assert Http.response.status_code == 200


def test_star_import_exports_only_the_public_api():
    ns = {}
    exec("from safetydance_django.test import *", ns)
    assert set(ns) - {"__builtins__"} == {
        "And", "Given", "Http", "Then", "When", "test_context"}


def test_http_namespace_loads_from_the_entry_point():
    result = subprocess.run(
        [sys.executable, "-c", SCRIPT], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
