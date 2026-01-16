from dashboard.models import BaseProjection
from dashboard.api_views import MODULE_MAP
from django.shortcuts import render
from django.db.models import Q, Sum


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

    context = {"headline_stats": sums.items()}
    return render(request, "base.html", context=context)
