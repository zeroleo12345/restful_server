from urllib.parse import quote, unquote, urlparse, parse_qs


def url_encode(url):
    return quote(url)


def url_decode(url):
    return unquote(url)


def url_param(url, key, pos=0):
    """
    参考:  https://docs.python.org/2/library/urlparse.html
    :param url: full url address
    :param key: params name
    :param pos: choose the position of the same params name
    :return: success: str, auto decode string like: %3A%2F%2F. it is char of '://'
                      None, when not find
    """
    parse_result = urlparse(url)
    params = parse_qs(parse_result.query, keep_blank_values=True)       # 字典: {'message': ['1']}
    if key in params:
        return params[key][pos]
    else:
        return None
