import os
import subprocess
import sys

from django.urls import reverse
import pytest
from safetydance import StepNotFound
from safetydance_django.test import *

SCRIPT = """
from safetydance import Given
import safetydance_django.test
assert Given.http.get.__module__ == "safetydance_django.steps"
"""


@pytest.mark.django_db
@test_context
def test_get():
    Given.http.get(reverse("simple-list"))
    Then.http.status_code_is(200)


def test_full_module_path_is_not_registered():
    with pytest.raises(StepNotFound):
        When.safetydance_django.steps.get


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


def test_importing_the_test_module_registers_http():
    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    result = subprocess.run(
        [sys.executable, "-c", SCRIPT], capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr


def test_bare_names_are_not_registered():
    with pytest.raises(StepNotFound):
        Given.get
