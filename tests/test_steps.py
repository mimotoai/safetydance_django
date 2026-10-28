from django.urls import reverse
import pytest
from safetydance import ContextDataNotSet, test_context
from safetydance_django.steps import *


def user_fields(username):
    return {"username": username, "email": "", "first_name": "", "last_name": ""}


@pytest.mark.django_db
@test_context
def test_get():
    get(reverse("simple-list"))
    status_code_is(200)


@pytest.mark.django_db
@test_context
def test_each_test_starts_without_a_response():
    with pytest.raises(ContextDataNotSet):
        Http.response


@pytest.mark.django_db
@test_context
def test_client_is_created_once_per_context():
    assert Http.client is Http.client
    assert Http.client.handler.enforce_csrf_checks is False


@pytest.mark.django_db
@test_context
def test_defaults_are_merged():
    defaults(HTTP_ACCEPT="application/json")
    defaults(HTTP_X_A="1")
    assert Http.client.defaults == {"HTTP_ACCEPT": "application/json", "HTTP_X_A": "1"}


@pytest.mark.django_db
@test_context
def test_status_code_is_reports_a_mismatch():
    get(reverse("simple-list"))
    with pytest.raises(AssertionError):
        status_code_is(404)


@pytest.mark.django_db
@pytest.mark.parametrize("codes", [(200,), (201, 200)])
@test_context
def test_status_code_is_one_of(codes):
    get(reverse("simple-list"))
    status_code_is_one_of(*codes)


@pytest.mark.django_db
@test_context
def test_response_json_is_matches_a_subset(django_user_model):
    django_user_model.objects.create(username="ada")
    get(reverse("user-list"))
    response_json_is([{"username": "ada"}])


@pytest.mark.django_db
@test_context
def test_response_data_is_ignores_id_and_url(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    get(reverse("user-detail", args=[ada.pk]))
    response_data_is(user_fields("ada"))


@pytest.mark.django_db
@test_context
def test_response_data_list_is_ignores_id_and_url(django_user_model):
    django_user_model.objects.create(username="ada")
    get(reverse("user-list"))
    response_data_list_is([user_fields("ada")])


@pytest.mark.django_db
@test_context
def test_post_then_get_created(django_user_model):
    post(reverse("user-list"), {"username": "grace"}, format="json")
    status_code_is(201)
    grace = django_user_model.objects.get(username="grace")
    response_location_header_is(
        "http://testserver" + reverse("user-detail", args=[grace.pk])
    )
    get_created()
    status_code_is(200)
    response_data_is(user_fields("grace"))


@pytest.mark.django_db
@test_context
def test_force_authenticate_applies_to_later_requests(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    force_authenticate(ada)
    get(reverse("user-list"))
    assert Http.response.renderer_context["request"].user == ada


def test_star_import_exports_only_the_public_api():
    import safetydance_django.steps as steps_module

    ns = {}
    exec("from safetydance_django.steps import *", ns)
    assert set(ns) - {"__builtins__"} == set(steps_module.__all__)
    assert "pytest" not in ns
    assert "APIClient" not in ns
