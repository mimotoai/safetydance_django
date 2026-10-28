=============================
safetydance_django Change Log
=============================

v0.1.0
====================

**Added:**

* A ``safetydance.steps`` entry point, ``http = "safetydance_django.steps"``,
  so the steps are found as ``Given.http.get`` and so on.
* ``safetydance_django.test`` re-exports ``Given``, ``When``, ``Then``,
  ``And``, ``test_context`` and ``Http``.
* The ``Http`` context data class holding ``Http.api_client`` and
  ``Http.response``.

**Changed:**

* Requires safetydance 0.5 or later (below 0.6) and Python 3.10 or later.
  The package is now built with uv and ``uv_build``. Version 0.0.6 was the
  Poetry release and has no changelog entry.
* HTTP state lives in the ``Http`` context data class as ``Http.api_client`` and
  ``Http.response``. The steps are registered under the ``http`` namespace
  through the ``safetydance.steps`` entry point, so ``Given.http.get`` works
  without importing ``safetydance_django``.
* The old default client received the context object as ``enforce_csrf_checks``.
  That object is truthy, so CSRF checks were effectively on. ``Http.api_client`` is
  now a plain ``APIClient()`` with CSRF checks off, as in the normal test
  client. Tests that relied on enforcement must build their own client:
  ``Http.api_client = APIClient(enforce_csrf_checks=True)``.
* ``Http.api_client`` is not called ``client`` because ``@test_context`` stores
  pytest fixtures by name, and pytest-django's ``client`` fixture silently
  replaced it.
* Importing ``safetydance_django.steps`` no longer needs configured Django
  settings; the ``APIClient`` import is deferred until a client is created.
* ``from safetydance_django.steps import *`` now exports only ``__all__``.
* Use the short namespace, ``Given.http.get`` and so on. The bare names
  (``get``, ``post``, ``put``, ``delete``, ``options``, ``head``, ``login``,
  ``defaults`` and so on) also resolve, but they raise ``AmbiguousStep`` as
  soon as any other step library defines the same name; safetydance imports
  every installed ``safetydance.steps`` entry point on the first lookup.

**Removed:**

* The ``safetydance_test`` and ``type_extensions`` dependencies.
* ``pytest`` and ``pytest-django`` are no longer installed as dependencies of
  safetydance-django. Install them in your own project.
* The ``http_client`` and ``http_response`` context keys. Use ``Http.api_client``
  and ``Http.response``.

**Fixed:**

* ``response_data_is`` and ``response_data_list_is`` raised ``NameError``
  (``self.content_type_is``).
* ``dictionaries_match`` (and so ``response_json_is``) returns ``False``
  instead of raising ``AttributeError`` when the observed value is not a
  mapping.
* ``status_code_is`` and ``status_code_is_one_of`` fail with an
  ``AssertionError`` on responses without a ``data`` attribute, and their
  message names the expected and received status codes.
* ``response_json_is`` shows the expected and observed JSON when it fails.

**Migrating:**

For projects such as scrud-django and django-scoped-rbac.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Old
     - New
   * - ``from safetydance_test import Given, When, Then, And, scripted_test``
     - ``from safetydance_django.test import *`` (``Given``, ``When``,
       ``Then``, ``And``, ``test_context`` and ``Http``)
   * - ``@scripted_test``
     - ``@test_context``, placed below ``@pytest.mark.*`` and above any
       ``@mock.patch`` decorators
   * - bare ``http_response`` / ``http_client`` in steps or tests
     - ``Http.response`` / ``Http.api_client``
   * - ``from safetydance_django.steps import http_client, http_response``
     - ``from safetydance_django.steps import Http``
   * - ``from safetydance_django.test import http_response``
     - ``from safetydance_django.test import Http`` (or ``import *``), then
       ``Http.response``
   * - ``http_response = http_client.put(...)`` (bare assignment)
     - ``Http.response = Http.api_client.put(...)``
   * - ``from safetydance_django.steps import *``
     - exports only ``__all__`` now: the steps and ``Http``, not
       ``http_client``, ``http_response`` or the modules' own imports
   * - ``step_data(T, initializer=f)``
     - a field in a ``@context_data`` class, using
       ``initializer(lambda ctx: ...)``, for example
       ``faker: Faker = initializer(lambda ctx: Faker())``
   * - ``step_data(T)`` without an initializer
     - an annotated field with no value, ``name: T``; reading it before it is
       set raises ``ContextDataNotSet``
   * - module-level ``step_data`` used like a dict
       (``named_instances["x"] = ...``)
     - a field on a ``@context_data`` class, ``named_instances: dict =
       initializer(lambda ctx: {})``, then ``MyData.named_instances["x"]``
   * - ``from safetydance import step`` (the old rewriting decorator)
     - ``from safetydance import step`` is now a plain registrar: it returns
       the function unchanged and does not rewrite its body. Use
       ``step_namespace(...)`` to add a short namespace.
   * - ``TestStepPrefix``
     - not needed: ``Given``, ``When``, ``Then`` and ``And`` are one
       ``StepPrefix`` instance (``from safetydance import StepPrefix`` if you
       need the type).
   * - ``all_steps_as_step_extensions_from(steps)``
     - decorate the module's steps with ``@step``, or ``register_steps(...)``
   * - ``step_extension(f, target_type=Http)``
     - ``@step_namespace("http")``, or explicit
       ``register_steps(f, namespace="http")``
   * - plain ``@step_extension`` (no ``target_type``)
     - ``@step``, giving a bare name such as ``Given.an_instance_named``, or
       ``@step_namespace("<ns>")`` to group the steps under ``Given.<ns>``
   * - a local ``context`` read inside a scripted test (``context.get(key)``)
     - ``get_context()`` or a ``@context_data`` field. Nested scripts no
       longer see their caller's data.

Step modules that are not exposed through a ``safetydance.steps`` entry point
register their steps only when they are imported, so import them in
``conftest.py``.

v0.0.5
====================



v0.0.4
====================



v0.0.3
====================



v0.0.2
====================



v0.0.1
====================


