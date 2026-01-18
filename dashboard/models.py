from django.db import models
from django.contrib.postgres.functions import RandomUUID


class Region(models.Model):
    """Geographic regions from GLOBIOM model."""

    code = models.CharField(
        max_length=10, unique=True, help_text="Region code (e.g., ame, anz)"
    )
    name = models.CharField(max_length=100, help_text="Full region name")

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class BaseProjection(models.Model):
    """Abstract base model for all projection data."""

    VARIABLE_UNIT_MAPPING = {
        "area": "1000 ha",
        "prod": "1000 t",
        "yild": "t/ha",
        "cons": "1000 t",
        "food": "1000 t",
        "feed": "1000 t",
        "othu": "1000 t",
        "expo": "1000 t",
        "impo": "1000 t",
        "nett": "1000 t",
        "land": "1000 ha",
    }

    class AllItemChoices(models.TextChoices):
        WHEAT = "wht", "Wheat"
        RICE = "ric", "Rice"
        COARSE_GRAINS = "cgr", "Coarse Grains"
        OILSEEDS = "osd", "Oilseeds"
        VEG_FRUIT_NUTS = "vfn", "Vegetables, Fruits & Nuts"
        RUMINANTS = "rum", "Ruminant Meat"
        NON_RUMINANTS = "nrm", "Non-Ruminant Meat & Eggs"
        DAIRY = "dry", "Dairy"
        SUGARCANE = "sgc", "Sugarcane"
        PLANT_FIBER = "pfb", "Plant-Based Fiber"
        CROPLAND = "crp", "Cropland"
        FOREST = "for", "Forest"
        GRASSLAND = "grs", "Grassland"
        NATURAL_LAND = "nld", "Other Natural Land"

    class UnitChoices(models.TextChoices):
        HECTARES = "ha", "Hectares"
        TONNES = "t", "Tonnes"
        TONNES_PER_HECTARE = "t/ha", "Tonnes per Hectare"

    # Subclasses must define ItemChoices and VariableChoices
    ItemChoices = None

    class VariableChoices(models.TextChoices):
        AREA = "area", "Area"
        PRODUCTION = "prod", "Production"
        YIELD = "yild", "Yield"
        CONSUMPTION = "cons", "Total Consumption"
        FOOD = "food", "Food Consumption"
        FEED = "feed", "Feed Use"
        OTHER_USE = "othu", "Other Uses"
        EXPORTS = "expo", "Exports"
        IMPORTS = "impo", "Imports"
        NET_TRADE = "nett", "Net Trade"

    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    year = models.IntegerField(help_text="Projection year")
    value = models.FloatField(help_text="Projected value")
    unit = models.CharField(max_length=20, choices=UnitChoices.choices)
    item = models.CharField(max_length=10, help_text="Item type")
    variable = models.CharField(max_length=10, help_text="Variable type")
    uuid = models.UUIDField(db_default=RandomUUID(), editable=False, db_index=True)

    class Meta:
        abstract = True
        ordering = ["year"]

    def __str__(self):
        item_label = (
            self.ItemChoices(self.item).label if self.ItemChoices else self.item
        )
        variable_label = (
            self.VariableChoices(self.variable).label
            if self.VariableChoices
            else self.variable
        )
        return f"{self.region.name} - {item_label} {variable_label} ({self.year})"


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

    class Meta:
        verbose_name = "Crop Module Projection"
        verbose_name_plural = "Crop Module Projections"
        indexes = [
            models.Index(fields=["region", "item", "year"]),
            models.Index(fields=["item", "variable"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(item__in=["wht", "ric", "cgr", "osd", "vfn"]),
                name="cropmodule_valid_item",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    variable__in=[
                        "area",
                        "prod",
                        "yild",
                        "cons",
                        "food",
                        "feed",
                        "othu",
                        "expo",
                        "impo",
                        "nett",
                    ]
                ),
                name="cropmodule_valid_variable",
            ),
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

    class Meta:
        verbose_name = "Animal Module Projection"
        verbose_name_plural = "Animal Module Projections"
        indexes = [
            models.Index(fields=["region", "item", "year"]),
            models.Index(fields=["item", "variable"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(item__in=["rum", "nrm", "dry", "grs"]),
                name="animalmodule_valid_item",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    variable__in=[
                        "area",
                        "prod",
                        "yild",
                        "cons",
                        "food",
                        "othu",
                        "expo",
                        "impo",
                        "nett",
                    ]
                ),
                name="animalmodule_valid_variable",
            ),
        ]


class BioenergyModule(BaseProjection):
    """
    Bioenergy module data from GLOBIOM.
    Covers: sugarcane (sgc), plant-based fiber (pfb).
    """

    class ItemChoices(models.TextChoices):
        SUGARCANE = "sgc", "Sugarcane"
        PLANT_FIBER = "pfb", "Plant-Based Fiber"

    class Meta:
        verbose_name = "Bioenergy Module Projection"
        verbose_name_plural = "Bioenergy Module Projections"
        indexes = [
            models.Index(fields=["region", "item", "year"]),
            models.Index(fields=["item", "variable"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(item__in=["sgc", "pfb"]),
                name="bioenergymodule_valid_item",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    variable__in=[
                        "area",
                        "prod",
                        "yild",
                        "cons",
                        "othu",
                        "expo",
                        "impo",
                        "nett",
                    ]
                ),
                name="bioenergymodule_valid_variable",
            ),
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
        indexes = [
            models.Index(fields=["region", "item", "year"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(item__in=["crp", "for", "grs", "nld"]),
                name="landcover_valid_item",
            ),
            models.CheckConstraint(
                condition=models.Q(variable__in=["land"]),
                name="landcover_valid_variable",
            ),
        ]
