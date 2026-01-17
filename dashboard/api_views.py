"""
API views for the dashboard application.

Provides JSON endpoints for regions, modules, and projection data.
"""

from django.db.models.query_utils import Q

from django.db.models import Sum

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import (
    Region,
    CropModule,
    AnimalModule,
    BioenergyModule,
    LandCover,
)


MODULE_MAP = {
    "crop": CropModule,
    "animal": AnimalModule,
    "bioenergy": BioenergyModule,
    "landcover": LandCover,
}


@require_GET
def projections_list(request):
    """
    GET /api/projections/

    Query parameters:
        - module (required): crop, animal, bioenergy, or landcover
        - region: Filter by region code
        - item: Filter by item code
        - variable: Filter by variable code
        - year_start: Filter years >= this value
        - year_end: Filter years <= this value

    Returns projection data as a JSON array.
    """
    params, error_response = _validate_projections_params(request)
    if error_response:
        return error_response

    model_class = params["model_class"]
    queryset = model_class.objects.select_related("region")

    # Apply filters
    if params["region"]:
        queryset = queryset.filter(region__code=params["region"])
    if params["item"]:
        queryset = queryset.filter(item=params["item"])
    if params["variable"]:
        queryset = queryset.filter(variable=params["variable"])
    if params["year_start"]:
        queryset = queryset.filter(year__gte=params["year_start"])
    if params["year_end"]:
        queryset = queryset.filter(year__lte=params["year_end"])

    # Build response data
    projections = []
    for obj in queryset:
        projections.append(
            {
                "uuid": str(obj.uuid),
                "region": obj.region.code,
                "region_name": obj.region.name,
                "year": obj.year,
                "item": obj.item,
                "item_label": obj.ItemChoices(obj.item).label,
                "variable": obj.variable,
                "variable_label": obj.VariableChoices(obj.variable).label,
                "value": obj.value,
                "unit": obj.unit,
            }
        )

    return JsonResponse({"projections": projections})
