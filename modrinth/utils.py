import re
from typing import Optional
from urllib import parse


def format_params(params: dict) -> str:
    _params_list = [f"{key}={str(value)}" for key, value in params.items()]
    _params = "&".join(_params_list).replace("'", '"')

    return _params


def build_url(base_url: str, endpoint: str, params: Optional[dict] = None) -> str:
    _base_url = base_url.strip()
    _base_url = re.sub(r":/+", "://", _base_url)

    _endpoint = parse.urlparse(_base_url).path
    _endpoint += endpoint.strip()
    _endpoint = re.sub(r"/+", "/", _endpoint)
    _endpoint = re.sub(r"/+$", "", _endpoint)

    url = parse.urljoin(_base_url, _endpoint)

    if params:
        return f"{url}?{format_params(params)}"

    return url
