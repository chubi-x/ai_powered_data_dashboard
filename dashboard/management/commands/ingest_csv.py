"""
Management command to ingest GLOBIOM projection data from CSV.

Reads data.csv and populates the appropriate projection models based on item codes.
Normalizes values from '1000 ha' and '1000 t' to actual ha and t.
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from dashboard.models import (
    AnimalModule,
    BioenergyModule,
    CropModule,
    LandCover,
    Region,
)

# Map item codes to their target model
# Note: "grs" is handled specially in _get_model_for_row() since it can be
# either AnimalModule (grazing area) or LandCover (land classification)
ITEM_TO_MODEL = {
    **dict.fromkeys(["wht", "ric", "cgr", "osd", "vfn"], CropModule),
    **dict.fromkeys(["rum", "nrm", "dry"], AnimalModule),
    **dict.fromkeys(["sgc", "pfb"], BioenergyModule),
    **dict.fromkeys(["crp", "for", "nld"], LandCover),
}


def _get_model_for_row(item: str, variable: str):
    """
    Determine target model based on item and variable.

    Most items map directly to a single model, but 'grs' (grassland) is special:
    - variable='land' -> LandCover (total grassland area as land classification)
    - variable='area' -> AnimalModule (grazing area for livestock)
    """
    if item == "grs":
        return LandCover if variable == "land" else AnimalModule
    return ITEM_TO_MODEL.get(item)


# Region code to full name mapping
REGION_NAMES = {
    "ame": "Africa & Middle East",
    "anz": "Oceania",
    "bra": "Brazil",
    "can": "Canada",
    "chn": "China",
    "eue": "EU Central/East",
    "eur": "Europe",
    "fsu": "Former USSR",
    "ind": "India",
    "men": "Middle East & North Africa",
    "nam": "North America",
    "oam": "Other Americas",
    "oas": "Other Asia",
    "osa": "Rest of South Asia",
    "sas": "South Asia",
    "sea": "Southeast Asia",
    "ssa": "Sub-Saharan Africa",
    "usa": "United States",
    "wld": "World",
}


class Command(BaseCommand):
    help = "Ingest GLOBIOM projection data from CSV into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default="data.csv",
            help="Path to the CSV file (default: data.csv)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before importing",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv"])

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self._clear_data()

        self.stdout.write(f"Reading data from {csv_path}...")

        try:
            with transaction.atomic():
                stats = self._ingest_csv(csv_path)
        except Exception as e:
            raise CommandError(f"Failed to ingest data: {e}")

        self.stdout.write(self.style.SUCCESS(f"\nIngestion complete!"))
        self.stdout.write(f"  Regions: {stats['regions']}")
        self.stdout.write(f"  CropModule: {stats['CropModule']}")
        self.stdout.write(f"  AnimalModule: {stats['AnimalModule']}")
        self.stdout.write(f"  BioenergyModule: {stats['BioenergyModule']}")
        self.stdout.write(f"  LandCover: {stats['LandCover']}")
        self.stdout.write(f"  Skipped: {stats['skipped']}")

    def _clear_data(self):
        """Clear all projection data."""
        for model in [CropModule, AnimalModule, BioenergyModule, LandCover, Region]:
            model.objects.all().delete()

    def _ingest_csv(self, csv_path: Path) -> dict:
        """Ingest CSV data and return statistics."""
        stats = {
            "regions": 0,
            "CropModule": 0,
            "AnimalModule": 0,
            "BioenergyModule": 0,
            "LandCover": 0,
            "skipped": 0,
        }

        # Cache for regions
        regions = {}

        # Batch objects for bulk_create
        batches = {
            CropModule: [],
            AnimalModule: [],
            BioenergyModule: [],
            LandCover: [],
        }

        batch_size = 1000

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                item = row["item"]
                variable = row["variable"]
                model_class = _get_model_for_row(item, variable)

                if model_class is None:
                    stats["skipped"] += 1
                    continue

                # Validate item and variable against model's choices
                if item not in model_class.ItemChoices.values:
                    self.stderr.write(
                        self.style.WARNING(f"Invalid item '{item}' for {model_class.__name__}, skipping")
                    )
                    stats["skipped"] += 1
                    continue
                if variable not in model_class.VariableChoices.values:
                    self.stderr.write(
                        self.style.WARNING(f"Invalid variable '{variable}' for {model_class.__name__}, skipping")
                    )
                    stats["skipped"] += 1
                    continue

                # Get or create region
                region_code = row["region"]
                if region_code not in regions:
                    region, created = Region.objects.get_or_create(
                        code=region_code,
                        defaults={"name": REGION_NAMES.get(region_code, region_code)},
                    )
                    regions[region_code] = region
                    if created:
                        stats["regions"] += 1

                # Normalize value and unit
                value = float(row["value"])
                unit = row["unit"]

                if unit == "1000 ha":
                    value *= 1000
                    unit = "ha"
                elif unit == "1000 t":
                    value *= 1000
                    unit = "t"
                # t/ha stays unchanged

                # Create model instance
                obj = model_class(
                    region=regions[region_code],
                    year=int(row["year"]),
                    value=value,
                    unit=unit,
                    item=item,
                    variable=variable,
                )

                batches[model_class].append(obj)

                # Bulk create when batch is full
                if len(batches[model_class]) >= batch_size:
                    model_class.objects.bulk_create(batches[model_class])
                    stats[model_class.__name__] += len(batches[model_class])
                    batches[model_class] = []

        # Insert remaining records
        for model_class, objects in batches.items():
            if objects:
                model_class.objects.bulk_create(objects)
                stats[model_class.__name__] += len(objects)

        return stats
