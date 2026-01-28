import socket
import urllib.request
import urllib.parse
import json

def get_hostname():
    """Отримати ім'я хоста."""
    return socket.gethostname()

def get_local_ip():
    """Отримати локальну IP-адресу."""
    try:
        # Створюємо сокет для отримання IP, не обов'язково підключатися
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def resolve_host(hostname):
    """Перетворити ім'я хоста в IP."""
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return None

def check_port(host, port, timeout=1.0):
    """Перевірити чи відкритий порт на хості."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, int(port)))
            return result == 0
    except Exception:
        return False

def scan_ports(host, start_port, end_port, timeout=0.1):
    """Сканувати діапазон портів на хості (повертає список відкритих)."""
    open_ports = []
    for port in range(int(start_port), int(end_port) + 1):
        if check_port(host, port, timeout):
            open_ports.append(port)
    return open_ports

def get_fqdn(name=""):
    """Отримати повне доменне ім'я (FQDN)."""
    return socket.getfqdn(name)

def http_get(url, params=None, headers=None, timeout=10):
    """Виконати GET-запит."""
    try:
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"
        
        req = urllib.request.Request(url)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "status": response.status,
                "body": response.read().decode('utf-8'),
                "headers": dict(response.info())
            }
    except Exception as e:
        return {"error": str(e), "status": 0}

def http_put(url, data=None, headers=None, is_json=True):
    """Виконати PUT-запит."""
    try:
        payload = None
        if data:
            if is_json:
                payload = json.dumps(data).encode('utf-8')
                if not headers: headers = {}
                headers['Content-Type'] = 'application/json'
            else:
                payload = urllib.parse.urlencode(data).encode('utf-8')

        req = urllib.request.Request(url, data=payload, method='PUT')
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "body": response.read().decode('utf-8'),
                "headers": dict(response.info())
            }
    except Exception as e:
        return {"error": str(e), "status": 0}

def http_patch(url, data=None, headers=None, is_json=True):
    """Виконати PATCH-запит."""
    try:
        payload = None
        if data:
            if is_json:
                payload = json.dumps(data).encode('utf-8')
                if not headers: headers = {}
                headers['Content-Type'] = 'application/json'
            else:
                payload = urllib.parse.urlencode(data).encode('utf-8')

        req = urllib.request.Request(url, data=payload, method='PATCH')
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "body": response.read().decode('utf-8'),
                "headers": dict(response.info())
            }
    except Exception as e:
        return {"error": str(e), "status": 0}

def http_delete(url, params=None, headers=None):
    """Виконати DELETE-запит."""
    try:
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"
        
        req = urllib.request.Request(url, method='DELETE')
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        
        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "body": response.read().decode('utf-8'),
                "headers": dict(response.info())
            }
    except Exception as e:
        return {"error": str(e), "status": 0}

def http_post(url, data=None, headers=None, is_json=True):
    """Виконати POST-запит."""
    try:
        payload = None
        if data:
            if is_json:
                payload = json.dumps(data).encode('utf-8')
                if not headers: headers = {}
                headers['Content-Type'] = 'application/json'
            else:
                payload = urllib.parse.urlencode(data).encode('utf-8')

        req = urllib.request.Request(url, data=payload, method='POST')
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        with urllib.request.urlopen(req) as response:
            return {
                "status": response.status,
                "body": response.read().decode('utf-8'),
                "headers": dict(response.info())
            }
    except Exception as e:
        return {"error": str(e), "status": 0}
