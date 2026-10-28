==================
safetydance_django
==================

Django and Django REST framework test steps for `safetydance
<https://pypi.org/project/safetydance/>`_. Drive an ``APIClient`` with
``Given.http.get(...)``, ``When.http.post(...)`` and check the response with
``Then.http.status_code_is(...)``.

Install
=======

.. code-block:: bash

    pip install safetydance-django

This needs Python 3.10 or later and safetydance 0.5. The example below also
needs ``pytest`` and ``pytest-django``, which are not installed as dependencies
of safetydance-django.

Example
=======

.. code-block:: python

    from django.urls import reverse
    import pytest
    from safetydance_django.test import *


    @pytest.mark.django_db
    @test_context
    def test_get():
        Given.http.get(reverse("simple-list"))
        Then.http.status_code_is(200)
        assert Http.response.status_code == 200

``reverse("simple-list")`` refers to the example app in this repository's
tests. Substitute the URL name of one of your own views.

Use the short ``http`` namespace, as in ``Given.http.get``. The bare names
(``get``, ``post``, ``put``, ``delete``, ``options``, ``head``, ``login``,
``defaults`` and so on) also resolve, but they raise ``AmbiguousStep`` as soon
as any other installed or imported step library defines the same name.

``safetydance_django.test`` exports ``And``, ``Given``, ``Http``, ``Then``,
``When`` and ``test_context``. Put ``@test_context`` below any
``@pytest.mark.*`` decorators and above any ``@mock.patch`` decorators.
``Http.client`` (an ``APIClient``) and ``Http.response`` hold the HTTP state
of the current test.

Documentation
=============

Documentation on the project is at https://dcharbon.gitlab.io/safetydance_django.
