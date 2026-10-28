from collections import OrderedDict
from copy import deepcopy
from pprint import pformat
from django.http import HttpResponse
from rest_framework.test import APIClient
from safetydance import context_data, initializer, step_namespace

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


@context_data
class Http:
    client: APIClient = initializer(lambda ctx: APIClient())
    response: HttpResponse


@step
def defaults(**kwargs):
    Http.client.defaults = {**Http.client.defaults, **kwargs}

@step
def force_authenticate(*args, **kwargs):
    """Can be used by rest_framework.test.APIClient"""
    Http.client.force_authenticate(*args, **kwargs)

@step
def force_login(*args, **kwargs):
    """Can be used by django.test.Client"""
    Http.client.force_login(*args, **kwargs)

@step
def login(*args, **kwargs):
    Http.client.login(*args, **kwargs)

@step
def delete(*args, **kwargs):
    '''Perform HTTP DELETE'''
    Http.response = Http.client.delete(*args, **kwargs)

@step
def get(*args, **kwargs):
    '''Perform HTTP GET'''
    Http.response = Http.client.get(*args, **kwargs)

@step
def head(*args, **kwargs):
    '''Perform HTTP HEAD'''
    Http.response = Http.client.head(*args, **kwargs)

@step
def get_created(*args, **kwargs):
    '''Perform HTTP GET of `location` header.'''
    Http.response = Http.client.get(
            Http.response['location'],
            *args,
            **kwargs)

@step
def options(*args, **kwargs):
    Http.response = Http.client.options(*args, **kwargs)

@step
def post(*args, **kwargs):
    Http.response = Http.client.post(*args, **kwargs)

@step
def put(*args, **kwargs):
    Http.response = Http.client.put(*args, **kwargs)

@step
def status_code_is(expected):
    '''
    Check that the expected status code matches the received status code
    '''
    assert Http.response.status_code == expected,\
            pformat(Http.response.data) if Http.response.data is not None else ""

@step
def status_code_is_one_of(*expected):
    '''
    Check that the expected status code matches the received status code
    '''
    assert Http.response.status_code in expected,\
            pformat(Http.response.data) if Http.response.data is not None else ""



@step
def content_type_is(expected):
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
    assert json_values_match(expected, observed)

@step
def response_data_is(expected, excluded_fields=None):
    '''
    Check that the expected response json body matches the received response
    body.
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
    Check that the expected response json body matches the received response
    body.
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
    Check that the expected response json body matches the received response
    body.
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
        elif isinstance(item, OrderedDict):
            item = dict(item)

        list_observed.append(clean_item(item))

    for i, item in enumerate(list_expected):
        list_expected[i] = clean_item(item)

    assert list_expected == list_observed

@step
def response_url_is(url_expected):
    assert Http.response.url == url_expected

@step
def response_location_header_is(location_expected):
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
    if observed is None:
        return False
    for key, value in expected.items():
        if not json_values_match(value, observed.get(key)):
            return False
    return True
