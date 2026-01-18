import json
import requests
from django.http import HttpResponse, JsonResponse
from django.conf import settings


def get_tile_json(request):
    titiler_url = settings.TITILER_URL.rstrip("/")
    cog_url = "/data/raster_web_mercator.tif"
    tile_url = f"{titiler_url}/cog/WebMercatorQuad/tilejson.json?url={cog_url}"

    try:
        response = requests.get(tile_url, timeout=30)
        headers = response.headers
        response.raise_for_status()
        response = json.loads(response.content.decode("utf8"))
        tiles = response["tiles"]
        url = tiles[0]
        url = url.replace(
            "http://localhost:8080/cog/tiles/WebMercatorQuad", "/raster/tiles"
        )
        response["tiles"] = [url]
        return JsonResponse(response)

    except requests.RequestException as e:
        return HttpResponse(f"Error fetching tile", status=500)


def get_tiles(request, z, x, y):
    titiler_url = settings.TITILER_URL.rstrip("/")
    cog_url = "/data/raster_web_mercator.tif"
    tile_url = f"{titiler_url}/cog/tiles/WebMercatorQuad/{z}/{x}/{y}@1x?url={cog_url}"
    try:
        response = requests.get(tile_url, timeout=30)
        response.raise_for_status()

        # Return the tile with appropriate content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get("content-type", "image/png"),
        )

    except requests.RequestException as e:
        return HttpResponse(f"Error fetching tile", status=500)


def get_info(request):
    titiler_url = settings.TITILER_URL.rstrip("/")
    cog_url = "/data/raster_web_mercator.tif"
    info_url = f"{titiler_url}/cog/info?url={cog_url}"

    try:
        response = requests.get(info_url, timeout=30)
        response.raise_for_status()

        # Return the JSON info
        return HttpResponse(
            response.content,
            content_type=response.headers.get("content-type", "application/json"),
        )

    except requests.RequestException as e:
        return HttpResponse(f"Error fetching info", status=500)
