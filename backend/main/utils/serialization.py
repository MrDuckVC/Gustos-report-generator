import importlib
from typing import Any, Iterable, Mapping

from django.contrib.auth.models import User
from django.http import HttpRequest, QueryDict
from django.urls import ResolverMatch
from django.utils.datastructures import MultiValueDict


def serialize_value(value: Any) -> bool | int | float | str | list | dict:
    try:
        if type(value) in (bool, int, float, str):
            return value
        elif isinstance(value, HttpRequest):
            return serialize_request(value)
        # QueryDict is subclass of MultiValueDict.
        elif isinstance(value, MultiValueDict):
            return [[k, serialize_value(v)] for k, v in value.items()]
        elif isinstance(value, Mapping):
            return {k: serialize_value(v) for k, v in value.items()}
        elif isinstance(value, Iterable):
            return [serialize_value(v) for v in value]
    except:
        pass


def serialize_request(request: HttpRequest):
    result = dict()
    result["GET"] = serialize_value(request.GET.items())
    result["POST"] = serialize_value(request.POST.items())
    result["method"] = request.method
    result["content_type"] = request.content_type
    result["content_params"] = serialize_value(request.content_params)
    result["resolver_match"] = serialize_value(request.resolver_match.__dict__)
    result["COOKIES"] = serialize_value(request.COOKIES)
    result["user"] = request.user.id if request.user else None
    result["path"] = request.path
    result["path_info"] = request.path_info
    result["META"] = serialize_value(request.META)
    result["scheme"] = request.scheme

    return result


def deserialize_request(request: dict):
    result = HttpRequest()

    if "GET" in request:
        result.GET = QueryDict(mutable=True)
        for key, value in request["GET"]:
            result.GET.appendlist(key, value)
        result.GET._mutable = False

    if "POST" in request:
        result.POST = QueryDict(mutable=True)
        for key, value in request["POST"]:
            result.POST.appendlist(key, value)
        result.POST._mutable = False

    result.method = request["method"]
    result.content_type = request["content_type"]
    result.content_params = request["content_params"]

    func_path = request["resolver_match"]["_func_path"]
    module_name, func_name = func_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)

    result.resolver_match = ResolverMatch(
        func=func,
        args=request["resolver_match"]["args"],
        kwargs=request["resolver_match"]["kwargs"],
        url_name=request["resolver_match"]["url_name"],
        app_names=request["resolver_match"]["app_names"],
        namespaces=request["resolver_match"]["namespaces"],
        route=request["resolver_match"]["route"],
        tried=request["resolver_match"]["tried"],
        captured_kwargs=request["resolver_match"]["captured_kwargs"],
        extra_kwargs=request["resolver_match"]["extra_kwargs"],
    )
    result.COOKIES = request["COOKIES"]
    result.user = User.objects.get(id=request["user"]) if request["user"] else None
    result.path = request["path"]
    result.path_info = request["path_info"]
    result.META = request["META"]

    return result


def is_request(value):
    return isinstance(value, Mapping) and value.get("__type__") == HttpRequest.__name__
