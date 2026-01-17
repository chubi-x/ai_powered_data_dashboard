from typing import override
from django.db.models.expressions import Value
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET
from django.http import HttpResponse, HttpResponseBadRequest
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dashboard.models import BaseProjection, CropModule, Region
from dashboard.api_views import MODULE_MAP
from django.shortcuts import render
from django.db.models import Q, Sum, F


def headline_stats():
    """Get headline stats

    Returns aggregate of "value" fields across all modules
    """
    s = {
        f"{var}": Sum("value", filter=Q(variable=var))
        for var in ["yild", "cons", "nett", "prod"]
    }  # unpacks to {"yild": Sum("value",filter=Q(variable="yild"))}

    totals = {
        name: model_class.objects.aggregate(**s)
        for name, model_class in MODULE_MAP.items()
    }
    return totals


def _build_timeseries_chart():
    years = (
        CropModule.objects.order_by("year").values_list("year", flat=True).distinct()
    )
    data = (
        CropModule.objects.filter(item="wht", variable="nett")
        .values("year")
        .annotate(val=Sum("value"))
        .order_by("year")
    )
    timeseries = {
        year: [item["val"] for item in data if item["year"] == year] for year in years
    }
    df = pd.DataFrame.from_dict(data)
    # df = pd.DataFrame(timeseries)

    # fig = px.line(df, x="year", title="Timeseries of Yield across time")
    fig = px.line(df, x="year", y="val", log_y=False)
    fig.update_xaxes(type="category")
    return pio.to_html(fig, include_plotlyjs=False, full_html=False)


def _build_pie_chart():
    data = (
        CropModule.objects.filter(variable="yild")
        .values("item")
        .annotate(val=Sum("value"))
        .values("item", "val")
    )
    data = [
        {"item": CropModule.ItemChoices(row["item"]).label, "value": row["val"]}
        for row in data
    ]
    df = pd.DataFrame.from_dict(data)

    fig = px.pie(df, values="value", names="item")
    return pio.to_html(fig, include_plotlyjs=False, full_html=False)


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
                "label": model_class._meta.verbose_name.replace(
                    " Projection", ""
                ).replace("Module", ""),
                "filters": (
                    {"name": "Item", "values": items},
                    {"name": "Metric", "values": variables},
                ),
            }
        )
    return modules


@require_GET
def pie_chart(request):
    chart = _build_pie_chart()
    return HttpResponse(chart)


class GetChartsView(TemplateView):
    template_name = "includes/chart.html"

    def _validate_projections_params(self):
        """
        Validate query parameters for the projections endpoint.

        Raises exceptions if params are invalid
        """
        module_name = self.request.GET.get("module")

        # Validate module name
        if module_name not in MODULE_MAP:
            valid_modules = ", ".join(MODULE_MAP.keys())
            raise ValueError(
                f"Invalid module: {module_name}. Valid options: {valid_modules}"
            )

        model_class = MODULE_MAP[module_name]

        # Validate item if provided
        item = self.request.GET.get("item")
        if item:
            valid_items = [choice.value for choice in model_class.ItemChoices]
            if item not in valid_items:
                raise ValueError(
                    f"Invalid item: {item}. Valid options for {module_name}: {', '.join(valid_items)}"
                )

        # Validate variable if provided
        metric = self.request.GET.get("metric")
        if metric:
            _valid_metrics = [choice.value for choice in model_class.VariableChoices]
            if metric not in _valid_metrics:
                raise ValueError(
                    f"Invalid variable: {metric}. Valid options for {module_name}: {', '.join(_valid_metrics)}"
                )

        # Validate region if provided
        region = self.request.GET.get("region")
        if region:
            if not Region.objects.filter(code=region).exists():
                raise ValueError(f"Invalid region: {region}")

    @override
    def get(self, *args, **kwargs):
        try:
            self._validate_projections_params()
        except ValueError as e:
            return HttpResponseBadRequest(e)

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context


@require_GET
def timeseries_chart(request):
    chart = _build_timeseries_chart()
    return HttpResponse(chart)


@require_GET
def index(request):
    # the stats variable is a list of dictionaries with this shape:
    # {'yild': 9809.408128068997,
    # 'cons': 57381230328.983246,
    # 'nett': -532189530.2717648,
    # 'prod': 97803358918.64377,
    # 'land': 179035135709.94003}
    stats = list(headline_stats().values())
    keys = stats[0].keys()
    sums = {}
    for sum_key in keys:
        # gets stuff like "Net Consumption"
        label = BaseProjection.VariableChoices(sum_key).label
        sums[label] = (
            sum(sum_dict[sum_key] for sum_dict in stats if sum_dict[sum_key]),
            BaseProjection.VARIABLE_UNIT_MAPPING.get(sum_key),
        )

    context = {
        "headline_stats": sums.items(),
        "modules": modules_list(),
        "regions": Region.objects.all().values("code", "name"),
    }

    return render(request, "base.html", context=context)
