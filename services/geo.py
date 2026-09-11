"""IP geolocation via ipwho.is (free, no API key)."""

from ipaddress import ip_address

import requests
from django.core.cache import cache


def lookup_ip(ip):
    empty = {
        "country": "",
        "country_code": "",
        "continent": "",
        "city": "",
        "region": "",
        "postal": "",
        "lat": None,
        "lon": None,
        "isp": "",
        "org": "",
        "timezone_ip": "",
        "connection_type": "",
    }
    if not ip:
        return empty
    try:
        parsed = ip_address(ip)
        if parsed.is_private or parsed.is_loopback or parsed.is_reserved:
            data = dict(empty)
            data["country"] = "Local"
            return data
    except ValueError:
        return empty

    cache_key = f"geo:v2:{ip}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = dict(empty)
    try:
        response = requests.get(f"https://ipwho.is/{ip}", timeout=2.5)
        payload = response.json()
        if payload.get("success"):
            conn = payload.get("connection") or {}
            tz = payload.get("timezone") or {}
            data = {
                "country": (payload.get("country") or "")[:80],
                "country_code": (payload.get("country_code") or "")[:8],
                "continent": (payload.get("continent") or "")[:40],
                "city": (payload.get("city") or "")[:80],
                "region": (payload.get("region") or "")[:80],
                "postal": (payload.get("postal") or "")[:20],
                "lat": payload.get("latitude"),
                "lon": payload.get("longitude"),
                "isp": (conn.get("isp") or "")[:120],
                "org": (conn.get("org") or "")[:120],
                "timezone_ip": (tz.get("id") or "")[:64],
                "connection_type": (conn.get("type") or "")[:40],
            }
    except Exception:
        pass

    cache.set(cache_key, data, 60 * 60 * 24)
    return data
