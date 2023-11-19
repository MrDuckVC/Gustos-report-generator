import base64
import hashlib

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def script(path, **kwargs):
    url = staticfiles_storage.url(path)
    path = staticfiles_storage.path(path)

    with open(path, 'rb') as f:
        checksum = hashlib.sha384(f.read()).digest()
        integrity = base64.b64encode(checksum).decode('utf-8')

    return render_to_string("generator/script.html", {
        "src": url,
        "integrity": f"sha384-{integrity}",
        "kwargs": kwargs.items(),
    })
