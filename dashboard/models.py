from django.db import models


class Region(models.Model):
    """Geographic regions from GLOBIOM model."""

    code = models.CharField(max_length=10, unique=True, help_text="Region code (e.g., ame, anz)")
    name = models.CharField(max_length=100, help_text="Full region name")

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class BaseProjection(models.Model):
    """Abstract base model for all projection data."""

    class UnitChoices(models.TextChoices):
        HECTARES = "ha", "Hectares"
        TONNES = "t", "Tonnes"
        TONNES_PER_HECTARE = "t/ha", "Tonnes per Hectare"

    # Subclasses must define ItemChoices and VariableChoices
    ItemChoices = None
    VariableChoices = None

    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    year = models.IntegerField(help_text="Projection year")
    value = models.FloatField(help_text="Projected value")
    unit = models.CharField(max_length=20, choices=UnitChoices.choices)
    item = models.CharField(max_length=10, help_text="Item type")
    variable = models.CharField(max_length=10, help_text="Variable type")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.region.code} - {self.item} - {self.variable} ({self.year})"


class CropModule(BaseProjection):
    """
    Crop module data from GLOBIOM.
    Covers: wheat (wht), rice (ric), coarse grains (cgr), oilseeds (osd),
    vegetables/fruits/nuts (vfn).
    """

    class ItemChoices(models.TextChoices):
        WHEAT = "wht", "Wheat"
        RICE = "ric", "Rice"
        COARSE_GRAINS = "cgr", "Coarse Grains"
        OILSEEDS = "osd", "Oilseeds"
        VEG_FRUIT_NUTS = "vfn", "Vegetables, Fruits & Nuts"

    class VariableChoices(models.TextChoices):
        AREA = "area", "Harvested Area"
        PRODUCTION = "prod", "Production"
        YIELD = "yild", "Yield"
        CONSUMPTION = "cons", "Total Consumption"
        FOOD = "food", "Food Consumption"
        FEED = "feed", "Feed Use"
        OTHER_USE = "othu", "Other Uses"
        EXPORTS = "expo", "Exports"
        IMPORTS = "impo", "Imports"
        NET_TRADE = "nett", "Net Trade"

    class Meta:
        verbose_name = "Crop Module Projection"
        verbose_name_plural = "Crop Module Projections"
        ordering = ["region", "item", "variable", "year"]
        indexes = [
            models.Index(fields=["region", "item", "year"]),
            models.Index(fields=["item", "variable"]),
        ]


class AnimalModule(BaseProjection):
    """
    Animal module data from GLOBIOM.
    Covers: ruminants (rum), non-ruminants (nrm), dairy (dry), grassland as grazing (grs).
    """

    class ItemChoices(models.TextChoices):
        RUMINANTS = "rum", "Ruminant Meat"
        NON_RUMINANTS = "nrm", "Non-Ruminant Meat & Eggs"
        DAIRY = "dry", "Dairy"
        GRASSLAND = "grs", "Grassland (Grazing)"

    class VariableChoices(models.TextChoices):
        AREA = "area", "Grazing Area"  # Only for grs
        PRODUCTION = "prod", "Production"
        YIELD = "yild", "Yield"  # Only for dry
        CONSUMPTION = "cons", "Total Consumption"
        FOOD = "food", "Food Consumption"
        OTHER_USE = "othu", "Other Uses"
        EXPORTS = "expo", "Exports"
        IMPORTS = "impo", "Imports"
        NET_TRADE = "nett", "Net Trade"

    class Meta:
        verbose_name = "Animal Module Projection"
        verbose_name_plural = "Animal Module Projections"
        ordering = ["region", "item", "variable", "year"]
        indexes = [
            models.Index(fields=["region", "item", "year"]),
            models.Index(fields=["item", "variable"]),
        ]


class BioenergyModule(BaseProjection):
    """
    Bioenergy module data from GLOBIOM.
    Covers: sugarcane (sgc), plant-based fiber (pfb).
    """

    class ItemChoices(models.TextChoices):
        SUGARCANE = "sgc", "Sugarcane"
        PLANT_FIBER = "pfb", "Plant-Based Fiber"

    class VariableChoices(models.TextChoices):
        AREA = "area", "Harvested Area"
        PRODUCTION = "prod", "Production"
        YIELD = "yild", "Yield"
        CONSUMPTION = "cons", "Total Consumption"
        OTHER_USE = "othu", "Other Uses"
        EXPORTS = "expo", "Exports"
        IMPORTS = "impo", "Imports"
        NET_TRADE = "nett", "Net Trade"

    class Meta:
        verbose_name = "Bioenergy Module Projection"
        verbose_name_plural = "Bioenergy Module Projections"
        ordering = ["region", "item", "variable", "year"]
        indexes = [
            models.Index(fields=["region", "item", "year"]),
            models.Index(fields=["item", "variable"]),
        ]


class LandCover(BaseProjection):
    """
    Land cover data from GLOBIOM.
    Covers: cropland (crp), forest (for), grassland (grs), other natural land (nld).
    Only tracks 'land' variable (total area by land type).
    """

    class ItemChoices(models.TextChoices):
        CROPLAND = "crp", "Cropland"
        FOREST = "for", "Forest"
        GRASSLAND = "grs", "Grassland"
        NATURAL_LAND = "nld", "Other Natural Land"

    class VariableChoices(models.TextChoices):
        LAND = "land", "Land Area"

    class Meta:
        verbose_name = "Land Cover Projection"
        verbose_name_plural = "Land Cover Projections"
        ordering = ["region", "item", "year"]
        indexes = [
            models.Index(fields=["region", "item", "year"]),
        ]
