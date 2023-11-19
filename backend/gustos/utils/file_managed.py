PUBLIC_SCHEME = "public://"


def get_absolute_url(file_managed_uri: str | None) -> str | None:
    if file_managed_uri is None:
        return None
    if file_managed_uri.startswith(PUBLIC_SCHEME):
        return f"https://gustos.local/files/{file_managed_uri[len(PUBLIC_SCHEME):]}"
    return None
