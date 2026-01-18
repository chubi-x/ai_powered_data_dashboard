from dashboard.views import MODULE_MAP
from django.http import HttpResponse
from django.views.generic import TemplateView
from google import genai
from google.genai import types
from django.db.models import Sum
from dashboard.models import (
    BaseProjection,
)

import markdown
from django.conf import settings


def get_projection_data(
    module: str,
    item: str = None,
    variable: str = None,
    year: int = None,
    region: str = None,
):
    """
    Queries the agricultural projection database.

    Args:
        module: The module to query. Must be one of: "crop", "animal", "bioenergy", "landcover".
        item: The specific item code (e.g., "wht" for Wheat, "ric" for Rice, "rum" for Ruminants).
              See ItemChoices in models for full lists.
        variable: The metric code (e.g., "prod" for Production, "yild" for Yield, "area" for Area).
        year: The projection year (e.g., 2025, 2030).
        region: The region code (e.g., "ame" for Americas).

        All filters are optional. The user is not required to provide them, except the module.

    Returns:
        float: The sum of the value matching the query, or 0 if no data found.
    """

    model_class = MODULE_MAP.get(module.lower())
    if not model_class:
        return "Error: Invalid module specified."

    filters = {}
    if item:
        filters["item"] = item
    if variable:
        filters["variable"] = variable
    if year:
        filters["year"] = year
    if region:
        filters["region__code"] = region
    if filters:
        result = model_class.objects.filter(**filters).aggregate(total=Sum("value"))
    else:
        result = model_class.objects.aggregate(total=Sum("value"))

    val = result.get("total")
    return val if val is not None else 0.0


AI_FUNCTIONS = [get_projection_data]


class AskAiView(TemplateView):
    def _build_dynamic_system_instruction(self):
        """
        Dynamically builds the system prompt by scraping labels and codes
        from the Django models defined in MODULE_MAP.
        """
        instruction = [
            "You are an agricultural data assistant.",
            "When querying the database, you MUST map user terms to these exact codes.",
            "If the user asks for a specific module (e.g. 'crops'), use that module code.",
            "If the module is ambiguous, infer it from the Item requested (e.g. 'Wheat' implies the 'crop' module).",
            "",
            "### MODULES MAP:",
        ]

        for module_name, model_class in MODULE_MAP.items():
            verbose_name = model_class._meta.verbose_name
            instruction.append(f'- "{module_name}" ({verbose_name})')

        instruction.append("\n### ITEMS MAP (Item Name -> Code):")

        for module_name, model_class in MODULE_MAP.items():
            if hasattr(model_class, "ItemChoices") and model_class.ItemChoices:
                instruction.append(f"\n[Module: {module_name}]")
                for choice in model_class.ItemChoices:
                    instruction.append(f'- {choice.label} -> "{choice.value}"')

        instruction.append("\n### VARIABLES MAP (Metric -> Code):")

        for module_name, model_class in MODULE_MAP.items():
            choices_class = getattr(
                model_class, "VariableChoices", BaseProjection.VariableChoices
            )

            instruction.append(f"\n[Module: {module_name}]")
            for choice in choices_class:
                instruction.append(f'- {choice.label} -> "{choice.value}"')

        instruction.append(
            "\n### REGION: If the user is unclear about a region, assume they're asking about all regions"
        )
        instruction.append("\nIMPORTANT: Always answer in a helpful, concise manner.")

        return "\n".join(instruction)

    def post(self, request, *args, **kwargs):
        user_query = request.POST.get("query")

        if not user_query:
            return HttpResponse("Please ask a question.")

        client = genai.Client(api_key=settings.GOOGLE_API_KEY)

        system_instruction = self._build_dynamic_system_instruction()

        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_query,
                config=types.GenerateContentConfig(
                    tools=AI_FUNCTIONS,
                    system_instruction=system_instruction,
                ),
            )

            if response.text:
                response_html = markdown.markdown(response.text)
                return HttpResponse(response_html)
            else:
                return HttpResponse(
                    "I processed the data but couldn't generate a text summary."
                )
        except Exception as e:
            print(f"AI Error: {e}")
            return HttpResponse(
                "<span class='text-red-500'>Error processing request. Please try again.</span>"
            )
