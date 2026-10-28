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
* The default client no longer receives the context as ``enforce_csrf_checks``.
  ``Http.client`` is a plain ``APIClient()``, so CSRF checks are off, as in the
  normal test client.

**Removed:**

* The ``safetydance_test`` and ``type_extensions`` dependencies.
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
     - a ``@context_data`` field with ``initializer(f)``
   * - ``all_steps_as_step_extensions_from(steps)``
     - decorate the module's steps with ``@step``, or ``register_steps(...)``
   * - ``step_extension(f, target_type=Http)``
     - ``@step_namespace("http")``, or explicit
       ``register_steps(f, namespace="http")``
   * - a local ``context`` read inside a scripted test (``context.get(key)``)
     - ``get_context()`` or a ``@context_data`` field. Nested scripts no
       longer see their caller's data.

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


