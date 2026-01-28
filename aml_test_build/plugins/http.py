"""
HTTP модуль для AML: прості запити GET/POST без зовнішніх залежностей.
"""

from urllib import request, parse, error
import json

def _to_headers(h):
    if not h:
        return {}
    return dict(h)

def _response_to_dict(resp, body_bytes):
    try:
        status = getattr(resp, 'status', None) or resp.getcode()
    except Exception:
        status = None
    headers = {}
    try:
        # HTTPMessage behaves like a dict of lists
        for k, v in resp.headers.items():
            headers[k] = v
    except Exception:
        pass
    url = getattr(resp, 'url', None)
    body = body_bytes.decode(resp.headers.get_content_charset() or 'utf-8', errors='replace')
    return {"ok": (status is not None and 200 <= status < 300), "status": status, "headers": headers, "text": body, "url": url}

def get(url, headers=None, timeout=10.0):
    """Виконати GET-запит. Повертає словник: ok, status, headers, text, url або error."""
    req = request.Request(url, method='GET', headers=_to_headers(headers))
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return _response_to_dict(resp, data)
    except error.HTTPError as e:
        body = e.read() if hasattr(e, 'read') else b''
        d = _response_to_dict(e, body)
        d["ok"] = False
        d["error"] = str(e)
        return d
    except Exception as e:
        return {"ok": False, "error": str(e), "status": None, "headers": {}, "text": "", "url": url}

def post_json(url, obj, headers=None, timeout=10.0):
    """POST JSON. Повертає словник як у get()."""
    h = _to_headers(headers)
    h.setdefault('Content-Type', 'application/json')
    data = json.dumps(obj).encode('utf-8')
    req = request.Request(url, method='POST', headers=h, data=data)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return _response_to_dict(resp, data)
    except error.HTTPError as e:
        body = e.read() if hasattr(e, 'read') else b''
        d = _response_to_dict(e, body)
        d["ok"] = False
        d["error"] = str(e)
        return d
    except Exception as e:
        return {"ok": False, "error": str(e), "status": None, "headers": {}, "text": "", "url": url}

def post_form(url, data_dict, headers=None, timeout=10.0):
    """POST application/x-www-form-urlencoded."""
    h = _to_headers(headers)
    h.setdefault('Content-Type', 'application/x-www-form-urlencoded')
    data = parse.urlencode(data_dict or {}).encode('utf-8')
    req = request.Request(url, method='POST', headers=h, data=data)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return _response_to_dict(resp, data)
    except error.HTTPError as e:
        body = e.read() if hasattr(e, 'read') else b''
        d = _response_to_dict(e, body)
        d["ok"] = False
        d["error"] = str(e)
        return d
    except Exception as e:
        return {"ok": False, "error": str(e), "status": None, "headers": {}, "text": "", "url": url}