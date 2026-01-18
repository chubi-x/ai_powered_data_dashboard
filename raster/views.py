import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.conf import settings
from django.views import View


class ViewerProxyView(View):
    def get(self, request):
        titiler_url = settings.TITILER_URL.rstrip('/')
        cog_url = '/data/raster_web_mercator.tif'
        viewer_url = f"{titiler_url}/cog/viewer?url={cog_url}"

        try:
            response = requests.get(viewer_url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find and replace tile URLs in script tags
            for script in soup.find_all('script'):
                if script.string:
                    # Replace tile URLs
                    script.string = script.string.replace(
                        f"{titiler_url}/cog/tiles/",
                        "/raster/tiles/"
                    )

            # Return modified HTML
            return HttpResponse(str(soup), content_type='text/html')

        except requests.RequestException as e:
            return HttpResponse(f"Error fetching viewer: {e}", status=500)


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
