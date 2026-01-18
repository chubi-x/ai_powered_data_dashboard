from typing import override
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET
from django.http import HttpResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as plotly_graph
import plotly.io as pio
from .models import (
    BaseProjection,
    CropModule,
    Region,
    AnimalModule,
    BioenergyModule,
    LandCover,
)
from django.db.models import Q, Sum


MODULE_MAP = {
    "crop": CropModule,
    "animal": AnimalModule,
    "bioenergy": BioenergyModule,
    "landcover": LandCover,
}


def _modules_list():
    """
    Get modules

    Returns all 4 modules with their available items and variables.
    """
    modules = []
    all_option = [{"code": "all", "label": "All", "selected": True}]
    for module_name, model_class in MODULE_MAP.items():
        items = [
            {"code": choice.value, "label": choice.label, "selected": False}
            for choice in model_class.ItemChoices
        ]
        variables = [
            {"code": choice.value, "label": choice.label, "selected": False}
            for choice in model_class.VariableChoices
        ]
        modules.append(
            {
                "name": module_name,
                "label": model_class._meta.verbose_name.replace(
                    " Projection", ""
                ).replace("Module", ""),
                "filters": [
                    {"name": "Region", "values": all_option + get_regions()},
                    {"name": "Item", "values": all_option + items},
                    {"name": "Metric", "values": all_option + variables},
                ],
            }
        )
    return modules


def _headline_stats():
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


def get_regions():
    regions = list(Region.objects.values("code", "name"))
    for region in regions:
        region["selected"] = False
    return regions


def _build_chart_filters(params):
    filters = []
    metric = params.get("metric")
    item = params.get("item")
    region = params.get("region")
    module = params.get("module")
    if module:
        model_class = MODULE_MAP[module]
    if metric and metric != "all":
        filters.append(Q(variable=metric))
    if item and item != "all":
        filters.append(Q(item=item))
    if region and region != "all":
        filters.append(Q(region__code=region))
    return filters, model_class


def _build_timeseries_chart(filters, model_class):
    if not filters:
        data = (
            model_class.objects.values("year")
            .annotate(val=Sum("value"))
            .order_by("year")
        )
    else:
        data = (
            model_class.objects.filter(*filters)
            .values("year")
            .annotate(val=Sum("value"))
            .order_by("year")
        )
    df = pd.DataFrame.from_dict(data)

    if df.empty:
        df = {"value": [], "item": []}
        fig = plotly_graph.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
        )
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
    else:
        fig = px.line(df, x="year", y="val", log_y=False)
        fig.update_xaxes(type="category")
    return pio.to_html(fig, include_plotlyjs=False, full_html=False)


def _build_pie_chart(filters, model_class):
    if not filters:
        data = (
            model_class.objects.values("item")
            .annotate(val=Sum("value"))
            .values("item", "val")
            .order_by("item")
        )
    else:
        data = (
            model_class.objects.filter(*filters)
            .values("item")
            .annotate(val=Sum("value"))
            .values("item", "val")
            .order_by("item")
        )
    data = [
        {"item": model_class.ItemChoices(row["item"]).label, "value": row["val"]}
        for row in data
    ]
    df = pd.DataFrame.from_dict(data)
    if not df.empty:
        fig = px.bar(df, y="value", x="item")
    else:
        df = {"value": [], "item": []}
        fig = plotly_graph.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
        )
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
    return pio.to_html(fig, include_plotlyjs=False, full_html=False)


class IndexView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, *args, **kwargs):
        # the stats variable is a list of dictionaries with this shape:
        # {'yild': 9809.408128068997,
        # 'cons': 57381230328.983246,
        # 'nett': -532189530.2717648,
        # 'prod': 97803358918.64377,
        # 'land': 179035135709.94003}
        stats = list(_headline_stats().values())
        keys = stats[0].keys()
        sums = {}
        for sum_key in keys:
            # gets stuff like "Net Consumption"
            label = BaseProjection.VariableChoices(sum_key).label
            sums[label] = (
                sum(sum_dict[sum_key] for sum_dict in stats if sum_dict[sum_key]),
                BaseProjection.VARIABLE_UNIT_MAPPING.get(sum_key),
            )
        context = super().get_context_data(*args, **kwargs)
        context = {
            **context,
            "headline_stats": sums.items(),
            "default_module": _modules_list()[0],
            "modules": _modules_list(),
        }
        return context


class GetChartsView(TemplateView):
    template_name = "includes/chart.html"

    @override
    def get(self, request, *args, **kwargs):
        module = request.GET.get("module", "crop")
        modules_list = _modules_list()
        module = next(m for m in modules_list if m["name"] == module)
        context = self.get_context_data(**kwargs)

        metric = self._check_selected_filter("metric", module)
        self._check_selected_filter("item", module)
        self._check_selected_filter("region", module)

        context["metric"] = metric
        context["modules"] = modules_list
        context["module"] = module

        return self.render_to_response(context)

    def _check_selected_filter(self, name, module):
        """Check if a filter passed in query params and updates selected"""
        model_class = MODULE_MAP[module["name"]]
        filter = next(
            filter for filter in module["filters"] if filter["name"].lower() == name
        )
        index = module["filters"].index(filter)
        if filter := self.request.GET.get(name):
            for f in module["filters"][index]["values"]:
                if f["code"] == filter:
                    f["selected"] = True
            try:
                return model_class.VariableChoices(filter).label
            except ValueError, AttributeError:
                pass
        return module["filters"][index]["values"][0]["label"]


@require_GET
def pie_chart(request):
    params = request.GET
    filters, model_class = _build_chart_filters(params)
    chart = _build_pie_chart(filters, model_class)
    return HttpResponse(chart)


@require_GET
def timeseries_chart(request):
    params = request.GET
    filters, model_class = _build_chart_filters(params)
    chart = _build_timeseries_chart(filters, model_class)
    return HttpResponse(chart)
