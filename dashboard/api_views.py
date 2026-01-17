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
def regions_list(request):
    """
    GET /api/regions/

    Returns a list of all regions with their code and name.
    """
    regions = Region.objects.all().values("code", "name")
    return JsonResponse({"regions": list(regions)})


def modules_list():
    """
    Get modules

    Returns all 4 modules with their available items and variables.
    """
    modules = []

    for module_name, model_class in MODULE_MAP.items():
        items = [
            {"code": choice.value, "label": choice.label}
            for choice in model_class.ItemChoices
        ]
        variables = [
            {"code": choice.value, "label": choice.label}
            for choice in model_class.VariableChoices
        ]
        modules.append(
            {
                "name": module_name,
                "label": model_class._meta.verbose_name.replace(" Projection", ""),
                "items": items,
                "variables": variables,
            }
        )

    return JsonResponse({"modules": modules})


def _validate_projections_params(request):
    """
    Validate query parameters for the projections endpoint.

    Returns (params_dict, error_response) tuple.
    If validation fails, error_response is a JsonResponse with status 400.
    If validation succeeds, error_response is None.
    """
    module_name = request.GET.get("module")

    # Module is required
    if not module_name:
        return None, JsonResponse(
            {"error": "Missing required parameter: module"}, status=400
        )

    # Validate module name
    if module_name not in MODULE_MAP:
        valid_modules = ", ".join(MODULE_MAP.keys())
        return None, JsonResponse(
            {"error": f"Invalid module: {module_name}. Valid options: {valid_modules}"},
            status=400,
        )

    model_class = MODULE_MAP[module_name]

    # Validate item if provided
    item = request.GET.get("item")
    if item:
        valid_items = [choice.value for choice in model_class.ItemChoices]
        if item not in valid_items:
            return None, JsonResponse(
                {
                    "error": f"Invalid item: {item}. Valid options for {module_name}: {', '.join(valid_items)}"
                },
                status=400,
            )

    # Validate variable if provided
    variable = request.GET.get("variable")
    if variable:
        valid_variables = [choice.value for choice in model_class.VariableChoices]
        if variable not in valid_variables:
            return None, JsonResponse(
                {
                    "error": f"Invalid variable: {variable}. Valid options for {module_name}: {', '.join(valid_variables)}"
                },
                status=400,
            )

    # Validate region if provided
    region = request.GET.get("region")
    if region:
        if not Region.objects.filter(code=region).exists():
            return None, JsonResponse(
                {"error": f"Invalid region: {region}"}, status=400
            )

    # Validate year parameters
    year_start = request.GET.get("year_start")
    year_end = request.GET.get("year_end")

    if year_start:
        try:
            year_start = int(year_start)
        except ValueError:
            return None, JsonResponse(
                {"error": "year_start must be an integer"}, status=400
            )

    if year_end:
        try:
            year_end = int(year_end)
        except ValueError:
            return None, JsonResponse(
                {"error": "year_end must be an integer"}, status=400
            )

    if year_start and year_end and year_start > year_end:
        return None, JsonResponse(
            {"error": "year_start cannot be greater than year_end"}, status=400
        )

    return {
        "model_class": model_class,
        "region": region,
        "item": item,
        "variable": variable,
        "year_start": year_start,
        "year_end": year_end,
    }, None


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
