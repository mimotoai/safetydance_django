from unittest import mock

from django.http import HttpResponseRedirect, JsonResponse
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
    assert Http.api_client is Http.api_client
    assert Http.api_client.handler.enforce_csrf_checks is False


@pytest.mark.django_db
@test_context
def test_defaults_are_merged():
    defaults(HTTP_ACCEPT="application/json")
    defaults(HTTP_X_A="1")
    assert Http.api_client.defaults == {"HTTP_ACCEPT": "application/json", "HTTP_X_A": "1"}


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


@pytest.mark.django_db
@test_context
def test_client_fixture_does_not_replace_api_client(client):
    # @test_context stores fixtures by name; pytest-django's `client` fixture
    # must not shadow the APIClient.
    from rest_framework.test import APIClient

    assert isinstance(Http.api_client, APIClient)
    assert client is not Http.api_client


def test_steps_import_without_django_settings():
    import os
    import subprocess
    import sys

    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    result = subprocess.run(
        [sys.executable, "-c", "import safetydance_django.steps"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, result.stderr


def test_dictionaries_match_is_false_when_observed_is_not_a_mapping():
    for observed in ("text", 3, [1], ["a"]):
        assert dictionaries_match({"a": 1}, observed) is False


class _PlainResponse:
    """A response without DRF's ``data`` attribute."""

    status_code = 500


@test_context
def test_status_code_is_fails_with_assertion_error_on_non_drf_response():
    Http.response = _PlainResponse()
    with pytest.raises(AssertionError):
        status_code_is(200)
    with pytest.raises(AssertionError):
        status_code_is_one_of(200, 201)


@pytest.mark.django_db
@test_context
def test_response_json_is_failure_shows_expected_and_observed(django_user_model):
    django_user_model.objects.create(username="ada")
    get(reverse("user-list"))
    with pytest.raises(AssertionError) as info:
        response_json_is([{"username": "nobody"}])
    assert "nobody" in str(info.value)
    assert "ada" in str(info.value)


class _Marker:
    value = "real"


@test_context
@mock.patch.object(_Marker, "value", "patched")
def test_mock_patch_below_test_context_is_applied():
    assert _Marker.value == "patched"


@pytest.mark.django_db
@test_context
def test_delete(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    delete(reverse("user-detail", args=[ada.pk]))
    status_code_is(204)
    assert not django_user_model.objects.filter(pk=ada.pk).exists()


@pytest.mark.django_db
@test_context
def test_put(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    put(reverse("user-detail", args=[ada.pk]), {"username": "ada2"}, format="json")
    status_code_is(200)
    ada.refresh_from_db()
    assert ada.username == "ada2"


@pytest.mark.django_db
@test_context
def test_head():
    head(reverse("simple-list"))
    status_code_is(200)
    assert Http.response.content == b""


@pytest.mark.django_db
@test_context
def test_options():
    options(reverse("simple-list"))
    status_code_is(200)
    assert "GET" in Http.response["Allow"]


@pytest.mark.django_db
@test_context
def test_login_with_the_right_password(django_user_model):
    django_user_model.objects.create_user(username="ada", password="pw")
    login(username="ada", password="pw")
    assert "_auth_user_id" in Http.api_client.session


@pytest.mark.django_db
@test_context
def test_login_with_a_wrong_password_is_silently_not_logged_in(django_user_model):
    # The step discards the result of login(), so a wrong password does not fail it.
    django_user_model.objects.create_user(username="ada", password="pw")
    login(username="ada", password="wrong")
    assert "_auth_user_id" not in Http.api_client.session


@pytest.mark.django_db
@test_context
def test_force_login(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    force_login(ada)
    assert Http.api_client.session["_auth_user_id"] == str(ada.pk)


def test_assert_data_ignores_id_url_and_excluded_fields():
    assert_data({"a": 1, "id": 1}, {"a": 1, "url": "x"})
    assert_data({"a": 1, "b": 2}, {"a": 1, "b": 3}, excluded_fields=["b"])


def test_assert_data_reports_a_mismatch():
    with pytest.raises(AssertionError):
        assert_data({"a": 1}, {"a": 2})


def test_assert_data_does_not_mutate_its_inputs():
    expected = {"a": 1, "id": 1, "b": 2}
    observed = {"a": 1, "url": "x", "b": 3}
    assert_data(expected, observed, excluded_fields=["b"])
    assert expected == {"a": 1, "id": 1, "b": 2}
    assert observed == {"a": 1, "url": "x", "b": 3}


@pytest.mark.django_db
@test_context
def test_response_url_is_follows_a_real_redirect():
    get("/api/users")
    status_code_is(301)
    response_url_is("/api/users/")
    with pytest.raises(AssertionError):
        response_url_is("/elsewhere/")


@test_context
def test_response_url_is_with_a_redirect_response():
    Http.response = HttpResponseRedirect("/next/")
    response_url_is("/next/")


@pytest.mark.django_db
@test_context
def test_response_location_header_is_reports_a_mismatch():
    post(reverse("user-list"), {"username": "grace"}, format="json")
    with pytest.raises(AssertionError):
        response_location_header_is("http://testserver/api/users/999/")


@pytest.mark.django_db
@test_context
def test_response_data_is_reports_a_mismatch(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    get(reverse("user-detail", args=[ada.pk]))
    with pytest.raises(AssertionError):
        response_data_is(user_fields("grace"))


@pytest.mark.django_db
@test_context
def test_response_data_is_excluded_fields(django_user_model):
    ada = django_user_model.objects.create(username="ada")
    get(reverse("user-detail", args=[ada.pk]))
    response_data_is({"username": "ada"}, excluded_fields=["email", "first_name", "last_name"])


def _json_response_with_data(data):
    response = JsonResponse(data, safe=False)
    response.data = data
    return response


@test_context
def test_response_data_list_is_enveloped():
    Http.response = _json_response_with_data(
        [{"etag": "x", "content": {"id": 1, "name": "a"}}])
    response_data_list_is([{"name": "a"}])


@test_context
def test_response_data_list_is_reports_a_mismatch():
    Http.response = _json_response_with_data([{"name": "a"}])
    with pytest.raises(AssertionError):
        response_data_list_is([{"name": "b"}])
    with pytest.raises(AssertionError):
        response_data_list_is([{"name": "a"}, {"name": "a"}])


@test_context
def test_response_data_list_is_empty():
    Http.response = _json_response_with_data([])
    response_data_list_is([])
    with pytest.raises(AssertionError):
        response_data_list_is([{"name": "a"}])


@pytest.mark.django_db
@test_context
def test_content_type_is_reports_a_mismatch():
    get(reverse("simple-list"))
    content_type_is("application/json")
    with pytest.raises(AssertionError):
        content_type_is("text/html")


@pytest.mark.django_db
@test_context
def test_status_code_is_one_of_reports_a_mismatch():
    get(reverse("simple-list"))
    with pytest.raises(AssertionError):
        status_code_is_one_of(201, 204)


@pytest.mark.django_db
@test_context
def test_status_code_is_message_has_codes_and_body(django_user_model):
    django_user_model.objects.create(username="ada")
    get(reverse("user-list"))
    with pytest.raises(AssertionError) as info:
        status_code_is(404)
    assert "404" in str(info.value)
    assert "200" in str(info.value)
    assert "ada" in str(info.value)


@test_context
def test_status_code_message_on_a_non_drf_response():
    Http.response = _PlainResponse()
    with pytest.raises(AssertionError, match="500"):
        status_code_is(200)


@pytest.mark.django_db
@test_context
def test_defaults_reach_the_request_and_can_be_overridden():
    defaults(HTTP_X_TEST="1")
    get(reverse("simple-list"))
    assert Http.response.wsgi_request.META["HTTP_X_TEST"] == "1"
    defaults(HTTP_X_TEST="2")
    get(reverse("simple-list"))
    assert Http.response.wsgi_request.META["HTTP_X_TEST"] == "2"


@pytest.mark.parametrize("expected, observed, result", [
    ({"a": {"b": 1}}, {"a": {"b": 1, "c": 2}}, True),
    ({"a": {"b": 1}}, {"a": {"b": 2}}, False),
    ({"a": 1}, {}, False),
    ({"a": {"b": 1}}, {"a": {}}, False),
    ({"a": None}, {}, True),
    ({"a": None}, {"a": None}, True),
    ({"a": 1}, None, False),
    ({}, {"a": 1}, True),
    ({}, {}, True),
    ({"a": 1}, 1, False),
    ({"a": 1}, {"a": {"b": 1}}, False),
    ({"a": {"b": 1}}, {"a": 1}, False),
    ([1, 2], [1, 2], True),
    ([1, 2], [2, 1], False),
    ([1, 2], [1, 2, 3], False),
    ([1, 2, 3], [1, 2], False),
    ([1], {"a": 1}, False),
    ([1], 1, False),
    ({"a": 1}, [1], False),
    ([], [], True),
    ([], [1], False),
    ([{"a": 1}], [{"a": 1, "b": 2}], True),
    ([{"a": 1}], [{"a": 2}], False),
    (1, 1, True),
    (1, 2, False),
    (None, None, True),
    (None, 0, False),
    ("a", "a", True),
])
def test_json_values_match_truth_table(expected, observed, result):
    assert json_values_match(expected, observed) is result


def test_lists_match_and_dictionaries_match_directly():
    assert lists_match([1], [1]) is True
    assert lists_match([1], (1,)) is False
    assert dictionaries_match({"a": 1}, {"a": 1}) is True
    assert dictionaries_match({"a": 1}, None) is False
