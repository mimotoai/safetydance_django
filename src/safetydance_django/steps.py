from collections.abc import Mapping
from copy import deepcopy
from pprint import pformat
from typing import TYPE_CHECKING
from django.http import HttpResponse
from safetydance import context_data, initializer, step_namespace

if TYPE_CHECKING:
    from rest_framework.test import APIClient

__all__ = [
    "Http",
    "defaults", "force_authenticate", "force_login", "login", "delete", "get",
    "head", "get_created", "options", "post", "put", "status_code_is",
    "status_code_is_one_of", "content_type_is", "response_json_is",
    "response_data_is", "assert_data", "response_data_list_is",
    "response_url_is", "response_location_header_is",
    "json_values_match", "lists_match", "dictionaries_match",
]

step = step_namespace("http")


def _new_api_client():
    # Imported here: rest_framework.test reads Django settings when imported.
    from rest_framework.test import APIClient

    return APIClient()


@context_data
class Http:
    """
    The HTTP state of the current test.

    ``api_client`` is a ``rest_framework.test.APIClient`` created on first use
    (CSRF checks off); ``response`` is the response of the last request step and
    is unset until one runs. The attribute is not called ``client`` because
    pytest-django's ``client`` fixture would replace it under ``@test_context``.
    """

    api_client: "APIClient" = initializer(lambda ctx: _new_api_client())
    response: HttpResponse


@step
def defaults(**kwargs):
    '''Merge `kwargs` into the client's default request arguments, such as
    ``HTTP_ACCEPT=...``, for every later request.'''
    Http.api_client.defaults = {**Http.api_client.defaults, **kwargs}

@step
def force_authenticate(*args, **kwargs):
    """Authenticate later requests as a user without logging in
    (``APIClient.force_authenticate``)."""
    Http.api_client.force_authenticate(*args, **kwargs)

@step
def force_login(*args, **kwargs):
    """Log a user in through the session without a password
    (``django.test.Client.force_login``)."""
    Http.api_client.force_login(*args, **kwargs)

@step
def login(*args, **kwargs):
    '''Log in with credentials (``django.test.Client.login``). The result is
    discarded, so a wrong password does not fail the step.'''
    Http.api_client.login(*args, **kwargs)

@step
def delete(*args, **kwargs):
    '''Perform HTTP DELETE'''
    Http.response = Http.api_client.delete(*args, **kwargs)

@step
def get(*args, **kwargs):
    '''Perform HTTP GET'''
    Http.response = Http.api_client.get(*args, **kwargs)

@step
def head(*args, **kwargs):
    '''Perform HTTP HEAD'''
    Http.response = Http.api_client.head(*args, **kwargs)

@step
def get_created(*args, **kwargs):
    '''Perform HTTP GET of the previous response's `Location` header.'''
    Http.response = Http.api_client.get(
            Http.response['location'],
            *args,
            **kwargs)

@step
def options(*args, **kwargs):
    '''Perform HTTP OPTIONS'''
    Http.response = Http.api_client.options(*args, **kwargs)

@step
def post(*args, **kwargs):
    '''Perform HTTP POST'''
    Http.response = Http.api_client.post(*args, **kwargs)

@step
def put(*args, **kwargs):
    '''Perform HTTP PUT'''
    Http.response = Http.api_client.put(*args, **kwargs)

def _status_message(expected):
    data = getattr(Http.response, "data", None)
    return (
        f"Expected status {expected!r}, got {Http.response.status_code}"
        + (f":\n{pformat(data)}" if data is not None else "")
    )


@step
def status_code_is(expected):
    '''
    Check that the expected status code matches the received status code
    '''
    assert Http.response.status_code == expected, _status_message(expected)

@step
def status_code_is_one_of(*expected):
    '''
    Check that the received status code is one of the expected status codes
    '''
    assert Http.response.status_code in expected, _status_message(expected)


@step
def content_type_is(expected):
    '''Check that the response has a Content-Type starting with `expected`.'''
    assert 'Content-Type' in Http.response
    assert Http.response['Content-Type'].startswith(expected)

@step
def response_json_is(expected):
    '''
    Check that the expected response json body matches the received response
    body.
    '''
    content_type_is('application/json')
    observed = Http.response.json()
    assert json_values_match(expected, observed), (
        f"Response JSON does not match.\nExpected:\n{pformat(expected)}\n"
        f"Observed:\n{pformat(observed)}"
    )

@step
def response_data_is(expected, excluded_fields=None):
    '''
    Check that the response's parsed `data` equals `expected`, after removing
    the `id` and `url` keys and any `excluded_fields` from both. The response
    must be JSON. Unlike response_json_is, the comparison is exact: observed
    keys that expected lacks fail it.
    '''
    def clean_item(obj):
        obj.pop('id', None)
        obj.pop('url', None)
        if excluded_fields is not None and isinstance(excluded_fields, list):
            for k in excluded_fields:
                obj.pop(k, None)
        return obj

    content_type_is('application/json')

    observed = clean_item(deepcopy(Http.response.data))
    expected = clean_item(deepcopy(expected))
    assert expected == observed

@step
def assert_data(expected, observed, excluded_fields=None):
    '''
    Check that `observed` equals `expected` after removing the `id` and `url`
    keys and any `excluded_fields` from both. Works on copies; the arguments are
    not modified.
    '''
    def clean_item(obj):
        obj.pop('id', None)
        obj.pop('url', None)
        if excluded_fields is not None and isinstance(excluded_fields, list):
            for k in excluded_fields:
                obj.pop(k, None)
        return obj

    observed = clean_item(deepcopy(observed))
    expected = clean_item(deepcopy(expected))
    assert expected == observed

@step
def response_data_list_is(list_expected, excluded_fields=None):
    '''
    Check that the response's data, a list, equals `list_expected` item by
    item, after removing the `id` and `url` keys and any `excluded_fields` from
    each. Items wrapped in an envelope (a dict with `etag` and `content`) are
    unwrapped first. The response must be JSON.
    '''
    def clean_item(obj):
        obj.pop('id', None)
        obj.pop('url', None)
        if excluded_fields is not None and isinstance(excluded_fields, list):
            for k in excluded_fields:
                obj.pop(k, None)
        return obj
    content_type_is('application/json')

    _list_observed = deepcopy(Http.response.data)
    list_expected = deepcopy(list_expected)

    list_observed = []

    is_enveloped = None

    for item in _list_observed:
        if is_enveloped is None:
            if 'etag' in item:
                is_enveloped = True
            else:
                is_enveloped = False
        if is_enveloped:
            item = item['content']
        elif isinstance(item, dict):
            item = dict(item)

        list_observed.append(clean_item(item))

    for i, item in enumerate(list_expected):
        list_expected[i] = clean_item(item)

    assert list_expected == list_observed

@step
def response_url_is(url_expected):
    '''Check the `url` of a redirect response, its target.'''
    assert Http.response.url == url_expected

@step
def response_location_header_is(location_expected):
    '''Check that the response's `Location` header equals `location_expected`.'''
    header = Http.response['location']
    assert header == location_expected


def json_values_match(expected, observed):
    '''
    Recursively walk the expected json value validating that the observed json
    value matches. Returns False on any missing or mismatched value.
    '''
    if isinstance(expected, list):
        return lists_match(expected, observed)
    if isinstance(expected, dict):
        return dictionaries_match(expected, observed)
    return expected == observed


def lists_match(expected, observed):
    '''
    Recursively walk the expected list validating that the observed list
    matches. Returns False on any missing or mismatched value.
    '''
    if not isinstance(observed, list):
        return False
    if len(expected) != len(observed):
        return False
    for i in range(0, len(expected)):
        if not json_values_match(expected[i], observed[i]):
            return False
    return True


def dictionaries_match(expected, observed):
    '''
    Recursively walk the expected dictionary validating that the observed
    dictionary matches. Returns False on any missing key or mismatched
    value.
    Note that keys that occur in observed or its nested dictionary objects
    that don't occur in expected or its matching nested dictionary objects
    are ignored.
    '''
    if not isinstance(observed, Mapping):
        return False
    for key, value in expected.items():
        if not json_values_match(value, observed.get(key)):
            return False
    return True
