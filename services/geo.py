"""IP geolocation via ipwho.is (free, no API key)."""

from ipaddress import ip_address

import requests
from django.core.cache import cache


def lookup_ip(ip):
    empty = {
        "country": "",
        "city": "",
        "region": "",
        "lat": None,
        "lon": None,
    }
    if not ip:
        return empty
    try:
        parsed = ip_address(ip)
        if parsed.is_private or parsed.is_loopback or parsed.is_reserved:
            return {
                "country": "Local",
                "city": "",
                "region": "",
                "lat": None,
                "lon": None,
            }
    except ValueError:
        return empty

    cache_key = f"geo:{ip}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = dict(empty)
    try:
        response = requests.get(f"https://ipwho.is/{ip}", timeout=2.5)
        payload = response.json()
        if payload.get("success"):
            data = {
                "country": (payload.get("country") or "")[:80],
                "city": (payload.get("city") or "")[:80],
                "region": (payload.get("region") or "")[:80],
                "lat": payload.get("latitude"),
                "lon": payload.get("longitude"),
            }
    except Exception:
        pass

    cache.set(cache_key, data, 60 * 60 * 24)
    return data
