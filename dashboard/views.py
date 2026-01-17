from django.views.decorators.http import require_GET
from django.http import HttpResponse
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dashboard.models import BaseProjection, CropModule
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


@require_GET
def pie_chart(request):
    chart = _build_pie_chart()
    return HttpResponse(chart)


@require_GET
def timeseries_chart(request):
    chart = _build_timeseries_chart()
    return HttpResponse(chart)


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
        # "initial_chart": build_timeseries_chart(),
    }
    return render(request, "base.html", context=context)
