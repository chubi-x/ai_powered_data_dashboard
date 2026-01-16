"""
Factory Boy factories for dashboard models.

Used for generating test data in unit tests.
"""

import factory
from factory import fuzzy

from .models import (
    Region,
    CropModule,
    AnimalModule,
    BioenergyModule,
    LandCover,
)


class RegionFactory(factory.django.DjangoModelFactory):
    """Factory for Region model."""
    
    class Meta:
        model = Region
        django_get_or_create = ("code",)
    
    code = factory.Sequence(lambda n: f"r{n:02d}")
    name = factory.LazyAttribute(lambda obj: f"Region {obj.code.upper()}")


class CropModuleFactory(factory.django.DjangoModelFactory):
    """Factory for CropModule model."""
    
    class Meta:
        model = CropModule
    
    region = factory.SubFactory(RegionFactory)
    year = fuzzy.FuzzyInteger(2020, 2050)
    value = fuzzy.FuzzyFloat(0.0, 10000.0)
    unit = CropModule.UnitChoices.HECTARES
    item = fuzzy.FuzzyChoice([choice.value for choice in CropModule.ItemChoices])
    variable = fuzzy.FuzzyChoice([choice.value for choice in CropModule.VariableChoices])


class AnimalModuleFactory(factory.django.DjangoModelFactory):
    """Factory for AnimalModule model."""
    
    class Meta:
        model = AnimalModule
    
    region = factory.SubFactory(RegionFactory)
    year = fuzzy.FuzzyInteger(2020, 2050)
    value = fuzzy.FuzzyFloat(0.0, 10000.0)
    unit = AnimalModule.UnitChoices.TONNES
    item = fuzzy.FuzzyChoice([choice.value for choice in AnimalModule.ItemChoices])
    variable = fuzzy.FuzzyChoice([choice.value for choice in AnimalModule.VariableChoices])


class BioenergyModuleFactory(factory.django.DjangoModelFactory):
    """Factory for BioenergyModule model."""
    
    class Meta:
        model = BioenergyModule
    
    region = factory.SubFactory(RegionFactory)
    year = fuzzy.FuzzyInteger(2020, 2050)
    value = fuzzy.FuzzyFloat(0.0, 10000.0)
    unit = BioenergyModule.UnitChoices.HECTARES
    item = fuzzy.FuzzyChoice([choice.value for choice in BioenergyModule.ItemChoices])
    variable = fuzzy.FuzzyChoice([choice.value for choice in BioenergyModule.VariableChoices])


class LandCoverFactory(factory.django.DjangoModelFactory):
    """Factory for LandCover model."""
    
    class Meta:
        model = LandCover
    
    region = factory.SubFactory(RegionFactory)
    year = fuzzy.FuzzyInteger(2020, 2050)
    value = fuzzy.FuzzyFloat(0.0, 10000.0)
    unit = LandCover.UnitChoices.HECTARES
    item = fuzzy.FuzzyChoice([choice.value for choice in LandCover.ItemChoices])
    variable = LandCover.VariableChoices.LAND  # Only one variable for LandCover
