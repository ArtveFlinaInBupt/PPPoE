# -*- coding: utf-8 -*-

from projection import Point2D

from typing import Any, Dict, List

import aiohttp
import asyncio
import json


def encap_geojson(points2d: List[Point2D]) -> Dict[str, Any]:
    """
    Encapsulate points in GeoJSON format.

    :param points2d: list of Point3D objects.
    :return: GeoJSON string.
    """
    return {
        'type': 'Polygon',
        'coordinates': [[(p.x, p.y) for p in points2d]]
    }


async def request(url, data):
    if not url.startswith('http://'):
        url = 'http://' + url
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
