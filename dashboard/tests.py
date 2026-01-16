"""
Unit tests for dashboard API endpoints.
"""

import json

from django.test import TestCase
from django.urls import reverse

from .factories import (
    RegionFactory,
    CropModuleFactory,
    AnimalModuleFactory,
    BioenergyModuleFactory,
    LandCoverFactory,
)


class RegionsAPITest(TestCase):
    """Tests for GET /api/regions/"""

    def test_empty_regions_list(self):
        """Returns empty list when no regions exist."""
        response = self.client.get(reverse("dashboard:api_regions"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["regions"], [])

    def test_returns_all_regions(self):
        """Returns all regions with code and name."""
        RegionFactory(code="usa", name="United States")
        RegionFactory(code="eur", name="Europe")
        RegionFactory(code="chn", name="China")

        response = self.client.get(reverse("dashboard:api_regions"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertEqual(len(data["regions"]), 3)
        # Regions are ordered by code
        codes = [r["code"] for r in data["regions"]]
        self.assertEqual(codes, ["chn", "eur", "usa"])

    def test_region_has_code_and_name(self):
        """Each region has code and name fields."""
        RegionFactory(code="bra", name="Brazil")

        response = self.client.get(reverse("dashboard:api_regions"))
        data = json.loads(response.content)

        region = data["regions"][0]
        self.assertIn("code", region)
        self.assertIn("name", region)
        self.assertEqual(region["code"], "bra")
        self.assertEqual(region["name"], "Brazil")


class ModulesAPITest(TestCase):
    """Tests for GET /api/modules/"""

    def test_returns_all_modules(self):
        """Returns all 4 modules."""
        response = self.client.get(reverse("dashboard:api_modules"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertEqual(len(data["modules"]), 4)
        module_names = [m["name"] for m in data["modules"]]
        self.assertIn("crop", module_names)
        self.assertIn("animal", module_names)
        self.assertIn("bioenergy", module_names)
        self.assertIn("landcover", module_names)

    def test_module_has_items_and_variables(self):
        """Each module has items and variables lists."""
        response = self.client.get(reverse("dashboard:api_modules"))
        data = json.loads(response.content)

        for module in data["modules"]:
            self.assertIn("name", module)
            self.assertIn("label", module)
            self.assertIn("items", module)
            self.assertIn("variables", module)
            self.assertIsInstance(module["items"], list)
            self.assertIsInstance(module["variables"], list)
            self.assertTrue(len(module["items"]) > 0)
            self.assertTrue(len(module["variables"]) > 0)

    def test_crop_module_items(self):
        """Crop module has correct items."""
        response = self.client.get(reverse("dashboard:api_modules"))
        data = json.loads(response.content)

        crop_module = next(m for m in data["modules"] if m["name"] == "crop")
        item_codes = [i["code"] for i in crop_module["items"]]
        self.assertEqual(set(item_codes), {"wht", "ric", "cgr", "osd", "vfn"})

    def test_item_has_code_and_label(self):
        """Each item has code and label fields."""
        response = self.client.get(reverse("dashboard:api_modules"))
        data = json.loads(response.content)

        crop_module = next(m for m in data["modules"] if m["name"] == "crop")
        for item in crop_module["items"]:
            self.assertIn("code", item)
            self.assertIn("label", item)


class ProjectionsAPITest(TestCase):
    """Tests for GET /api/projections/"""

    def setUp(self):
        """Create test data."""
        self.region_usa = RegionFactory(code="usa", name="United States")
        self.region_eur = RegionFactory(code="eur", name="Europe")

    def test_module_required(self):
        """Returns 400 if module parameter is missing."""
        response = self.client.get(reverse("dashboard:api_projections"))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertIn("module", data["error"].lower())

    def test_invalid_module(self):
        """Returns 400 for invalid module name."""
        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "invalid"}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertIn("invalid", data["error"].lower())

    def test_invalid_item(self):
        """Returns 400 for invalid item code."""
        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "item": "xyz"}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_invalid_variable(self):
        """Returns 400 for invalid variable code."""
        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "variable": "xyz"}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_invalid_region(self):
        """Returns 400 for invalid region code."""
        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "region": "xyz"}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_invalid_year_start(self):
        """Returns 400 if year_start is not an integer."""
        response = self.client.get(
            reverse("dashboard:api_projections"),
            {"module": "crop", "year_start": "abc"},
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("year_start", data["error"])

    def test_invalid_year_end(self):
        """Returns 400 if year_end is not an integer."""
        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "year_end": "abc"}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("year_end", data["error"])

    def test_year_start_greater_than_year_end(self):
        """Returns 400 if year_start > year_end."""
        response = self.client.get(
            reverse("dashboard:api_projections"),
            {"module": "crop", "year_start": "2030", "year_end": "2020"},
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("year_start", data["error"])

    def test_returns_projections_for_module(self):
        """Returns projections for the specified module."""
        CropModuleFactory(
            region=self.region_usa,
            year=2025,
            item="wht",
            variable="prod",
            value=1000.0,
            unit="t",
        )
        # Create a record in a different module - should not be returned
        AnimalModuleFactory(region=self.region_usa)

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertEqual(len(data["projections"]), 1)
        projection = data["projections"][0]
        self.assertEqual(projection["item"], "wht")
        self.assertEqual(projection["variable"], "prod")

    def test_filter_by_region(self):
        """Filters projections by region."""
        CropModuleFactory(region=self.region_usa, item="wht")
        CropModuleFactory(region=self.region_eur, item="ric")

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "region": "usa"}
        )
        data = json.loads(response.content)

        self.assertEqual(len(data["projections"]), 1)
        self.assertEqual(data["projections"][0]["region"], "usa")

    def test_filter_by_item(self):
        """Filters projections by item."""
        CropModuleFactory(region=self.region_usa, item="wht")
        CropModuleFactory(region=self.region_usa, item="ric")

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "item": "wht"}
        )
        data = json.loads(response.content)

        self.assertEqual(len(data["projections"]), 1)
        self.assertEqual(data["projections"][0]["item"], "wht")

    def test_filter_by_variable(self):
        """Filters projections by variable."""
        CropModuleFactory(region=self.region_usa, item="wht", variable="prod")
        CropModuleFactory(region=self.region_usa, item="wht", variable="area")

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop", "variable": "prod"}
        )
        data = json.loads(response.content)

        self.assertEqual(len(data["projections"]), 1)
        self.assertEqual(data["projections"][0]["variable"], "prod")

    def test_filter_by_year_range(self):
        """Filters projections by year range."""
        CropModuleFactory(region=self.region_usa, year=2020)
        CropModuleFactory(region=self.region_usa, year=2025)
        CropModuleFactory(region=self.region_usa, year=2030)
        CropModuleFactory(region=self.region_usa, year=2035)

        response = self.client.get(
            reverse("dashboard:api_projections"),
            {"module": "crop", "year_start": "2023", "year_end": "2032"},
        )
        data = json.loads(response.content)

        self.assertEqual(len(data["projections"]), 2)
        years = [p["year"] for p in data["projections"]]
        self.assertIn(2025, years)
        self.assertIn(2030, years)

    def test_projection_response_fields(self):
        """Projection response includes all expected fields."""
        CropModuleFactory(
            region=self.region_usa,
            year=2025,
            item="wht",
            variable="prod",
            value=1234.56,
            unit="t",
        )

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop"}
        )
        data = json.loads(response.content)

        projection = data["projections"][0]
        self.assertIn("uuid", projection)
        self.assertIn("region", projection)
        self.assertIn("region_name", projection)
        self.assertIn("year", projection)
        self.assertIn("item", projection)
        self.assertIn("item_label", projection)
        self.assertIn("variable", projection)
        self.assertIn("variable_label", projection)
        self.assertIn("value", projection)
        self.assertIn("unit", projection)

    def test_animal_module_projections(self):
        """Works with animal module."""
        AnimalModuleFactory(region=self.region_usa, item="rum", variable="prod")

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "animal"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["projections"]), 1)

    def test_bioenergy_module_projections(self):
        """Works with bioenergy module."""
        BioenergyModuleFactory(region=self.region_usa, item="sgc", variable="prod")

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "bioenergy"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["projections"]), 1)

    def test_landcover_module_projections(self):
        """Works with landcover module."""
        LandCoverFactory(region=self.region_usa, item="crp", variable="land")

        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "landcover"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["projections"]), 1)

    def test_empty_results(self):
        """Returns empty list when no projections match filters."""
        response = self.client.get(
            reverse("dashboard:api_projections"), {"module": "crop"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["projections"], [])
