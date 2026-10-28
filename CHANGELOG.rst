=============================
safetydance_django Change Log
=============================

.. current developments

v0.1.0
====================

**Changed:**

* Requires safetydance 0.5 or later (below 0.6) and Python 3.10 or later.
  The package is now built with uv and ``uv_build``. Version 0.0.6 was the
  Poetry release and has no changelog entry.
* HTTP state lives in the ``Http`` context data class as ``Http.client`` and
  ``Http.response``. The steps are registered under the ``http`` namespace
  through the ``safetydance.steps`` entry point, so ``Given.http.get`` works
  without importing ``safetydance_django``.
* The old default client received the context object as ``enforce_csrf_checks``.
  That object is truthy, so CSRF checks were effectively on. ``Http.client`` is
  now a plain ``APIClient()`` with CSRF checks off, as in the normal test
  client. Tests that relied on enforcement must build their own client:
  ``Http.client = APIClient(enforce_csrf_checks=True)``.
* Use the short namespace, ``Given.http.get`` and so on. The bare names
  (``get``, ``post``, ``put``, ``delete``, ``options``, ``head``, ``login``,
  ``defaults`` and so on) also resolve, but they raise ``AmbiguousStep`` as
  soon as any other installed or imported step library defines the same name.

**Removed:**

* The ``safetydance_test`` and ``type_extensions`` dependencies.
* ``pytest`` and ``pytest-django`` are no longer installed as dependencies of
  safetydance-django. Install them in your own project.
* The ``http_client`` and ``http_response`` context keys. Use ``Http.client``
  and ``Http.response``.

**Fixed:**

* ``response_data_is`` and ``response_data_list_is`` raised ``NameError``
  (``self.content_type_is``).

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
     - ``Http.response`` / ``Http.client``
   * - ``from safetydance_django.steps import http_client, http_response``
     - ``from safetydance_django.steps import Http``
   * - ``step_data(T, initializer=f)``
     - a field in a ``@context_data`` class, using
       ``initializer(lambda ctx: ...)``, for example
       ``faker: Faker = initializer(lambda ctx: Faker())``
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


