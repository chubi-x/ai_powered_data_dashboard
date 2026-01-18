import requests
from django.http import HttpResponse
from django.conf import settings
from django.views import View


class TileProxyView(View):
    def get(self, request, z, x, y):
        titiler_url = settings.TITILER_URL.rstrip('/')
        cog_url = '/data/raster_web_mercator.tif'
        tile_url = f"{titiler_url}/cog/tiles/{z}/{x}/{y}?url={cog_url}"

        try:
            response = requests.get(tile_url, timeout=30)
            response.raise_for_status()

            # Return the tile with appropriate content type
            return HttpResponse(
                response.content,
                content_type=response.headers.get('content-type', 'image/png')
            )

        except requests.RequestException as e:
            return HttpResponse(f"Error fetching tile: {e}", status=500)


class InfoProxyView(View):
    def get(self, request):
        titiler_url = settings.TITILER_URL.rstrip('/')
        cog_url = '/data/raster_web_mercator.tif'
        info_url = f"{titiler_url}/cog/info?url={cog_url}"

        try:
            response = requests.get(info_url, timeout=30)
            response.raise_for_status()

            # Return the JSON info
            return HttpResponse(
                response.content,
                content_type=response.headers.get('content-type', 'application/json')
            )

        except requests.RequestException as e:
            return HttpResponse(f"Error fetching info: {e}", status=500)
