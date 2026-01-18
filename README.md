# AI-Powered Data Dashboard

A Django-based data dashboard featuring agricultural projections visualization, raster rendering via TiTiler, and an AI chatbot.

## Tech Stack

- **Backend**: Django 5.x
- **Database**: PostgreSQL 15
- **Charts**: Plotly
- **Raster**: TiTiler + Leaflet
- **AI**: Google Gemini with function calling
- **Frontend**: Django Templates + HTMX

## Development Setup

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.11+ and uv for local development

### Quick Start (Docker)

1. Clone the repository and copy environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values (especially `GEMINI_API_KEY`)

3. Start the services:

   ```bash
   docker compose up
   ```

4. Access the applications:
   - Django: http://localhost:8000
   - TiTiler: http://localhost:8080/docs (API docs)

### Local Development (without Docker)

1. Create virtual environment and install dependencies:

   ```bash
   uv venv
   source .venv/bin/activate
   uv pip sync requirements.txt
   ```

2. Copy environment file and configure:

   ```bash
   cp .env.example .env
   # Edit .env - set POSTGRES_HOST=localhost
   ```

3. Start PostgreSQL (via Docker or locally):

   ```bash
   docker compose up db
   ```

4. Run migrations and start server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Loading Data

Load the CSV data into the database:

```bash
python manage.py ingest_csv
```

### Raster Setup

The raster file is served locally from `raster_data/raster_web_mercator.tif` via TiTiler.

**Background**: The original raster was obtained from an IIASA S3 bucket in EPSG:3035 (European Lambert Azimuthal Equal-Area projection). TiTiler could not reproject it on-the-fly, so it was manually reprojected to EPSG:3857 (Web Mercator) using GDAL:

```bash
gdalwarp -t_srs EPSG:3857 original.tif raster_web_mercator.tif
```

Access tiles via TiTiler:

- Tile URL: `http://localhost:8080/cog/tiles/{z}/{x}/{y}?url=/data/raster_web_mercator.tif`
- API docs: http://localhost:8080/docs

## Data Model Architecture

### Overview

The dashboard visualizes agricultural economic projections from the **AGLINK-COSIMO/GLOBIOM** integrated assessment model. The data covers years 2000-2040 across 19 global regions with 14 commodity types and 11 economic variables.

### Data Sources & Research

The data model was designed by cross-referencing official GLOBIOM documentation:

- [GLOBIOM Documentation (IIASA)](https://pure.iiasa.ac.at/id/eprint/18996/1/GLOBIOM_Documentation.pdf) - Primary source for crop/commodity mappings
- [MESSAGE-GLOBIOM Land Use Documentation](https://www.iamcdocumentation.eu/MESSAGE-GLOBIOM) - Land use classification reference
- [JRC GLOBIOM Deliverable D3.3](https://datam.jrc.ec.europa.eu/datam/perm/file/29fc34fd-4ef1-4d24-afab-81cdb005d397/Deliverable+D3.3.pdf) - Region abbreviations and commodity codes
- [ResearchSquare GLOBIOM Paper](https://assets-eu.researchsquare.com/files/rs-6009571/v1_covered_cb9dceab-cbc6-4254-815d-c16e0782d288.pdf?c=1759747798) - Additional commodity codes (pfb, vfn)

### Model Structure

```
BaseProjection (abstract)
├── region (FK)     → Region model
├── year            → Projection year (2000-2040)
├── value           → Projected value
├── unit            → ha | t | t/ha
├── item            → Commodity code
└── variable        → Economic variable

Concrete Models:
├── CropModule      → wht, ric, cgr, osd, vfn
├── AnimalModule    → rum, nrm, dry, grs
├── BioenergyModule → sgc, pfb
└── LandCover       → crp, for, grs, nld
```

### Item Code Mappings

| Code  | Description                                        | Module             |
| ----- | -------------------------------------------------- | ------------------ |
| `wht` | Wheat                                              | Crop               |
| `ric` | Rice                                               | Crop               |
| `cgr` | Coarse Grains (corn, millet, sorghum)              | Crop               |
| `osd` | Oilseeds (soybean, rapeseed, sunflower, groundnut) | Crop               |
| `vfn` | Vegetables, Fruits & Nuts                          | Crop               |
| `rum` | Ruminant Meat                                      | Animal             |
| `nrm` | Non-Ruminant Meat & Eggs                           | Animal             |
| `dry` | Dairy                                              | Animal             |
| `grs` | Grassland (Grazing)                                | Animal / LandCover |
| `sgc` | Sugarcane                                          | Bioenergy          |
| `pfb` | Plant-Based Fiber                                  | Bioenergy          |
| `crp` | Cropland                                           | LandCover          |
| `for` | Forest                                             | LandCover          |
| `nld` | Other Natural Land                                 | LandCover          |

### Variable Code Mappings

| Code   | Description            | Unit |
| ------ | ---------------------- | ---- |
| `area` | Harvested/Grazing Area | ha   |
| `prod` | Production             | t    |
| `yild` | Yield                  | t/ha |
| `cons` | Total Consumption      | t    |
| `food` | Food Consumption       | t    |
| `feed` | Feed Use               | t    |
| `othu` | Other Uses             | t    |
| `expo` | Exports                | t    |
| `impo` | Imports                | t    |
| `nett` | Net Trade              | t    |
| `land` | Land Area              | ha   |

### Region Codes

Mappings sourced from [GLOBIOM Documentation (IIASA)](https://pure.iiasa.ac.at/id/eprint/18996/1/GLOBIOM_Documentation.pdf) and [JRC Deliverable D3.3](https://datam.jrc.ec.europa.eu/datam/perm/file/29fc34fd-4ef1-4d24-afab-81cdb005d397/Deliverable+D3.3.pdf). Codes marked with \* are inferred.

| Code    | Region                     | Description                                                              |
| ------- | -------------------------- | ------------------------------------------------------------------------ |
| `bra`   | Brazil                     | Brazil                                                                   |
| `can`   | Canada                     | Canada                                                                   |
| `chn`   | China                      | China                                                                    |
| `ind`   | India                      | India                                                                    |
| `usa`   | United States              | United States of America                                                 |
| `fsu`   | Former USSR                | Russia, Ukraine, Armenia, Azerbaijan, Belarus, Georgia, Kazakhstan, etc. |
| `sea`   | Southeast Asia             | Indonesia, Malaysia, Philippines, Thailand, Vietnam, etc.                |
| `ssa`   | Sub-Saharan Africa         | Congo Basin, Eastern Africa, South Africa, West & Central Africa         |
| `men`   | Middle East & North Africa | Middle East, Northern Africa, Turkey                                     |
| `wld`   | World                      | Global aggregate                                                         |
| `anz`\* | Oceania                    | Australia, New Zealand, Pacific Islands                                  |
| `eue`\* | EU Central/East            | Bulgaria, Czech Republic, Hungary, Poland, Romania, Slovakia, Slovenia   |
| `eur`\* | Europe                     | EU aggregate                                                             |
| `nam`\* | North America              | USA + Canada aggregate                                                   |
| `oam`\* | Other Americas             | Argentina, Mexico, Rest of Central/South America                         |
| `oas`\* | Other Asia                 | Broader Asia aggregate                                                   |
| `osa`\* | Rest of South Asia         | Afghanistan, Bangladesh, Bhutan, Nepal, Pakistan, Sri Lanka              |
| `sas`\* | South Asia                 | India + Rest of South Asian States                                       |
| `ame`\* | Africa & Middle East       | Africa + Middle East aggregate                                           |

## Project Structure

```
├── config/          # Django settings (base, dev, production)
├── dashboard/       # Main dashboard app (charts, data views, models)
├── raster/          # Raster/map rendering app
├── chatbot/         # AI chatbot app
├── static/          # CSS, JS assets
└── raster_data/     # COG files for TiTiler
```

## Environment Variables

| Variable                 | Description                        | Default                   |
| ------------------------ | ---------------------------------- | ------------------------- |
| `SECRET_KEY`             | Django secret key                  | (insecure default)        |
| `DJANGO_SETTINGS_MODULE` | Settings module                    | `config.dev`              |
| `POSTGRES_DB`            | Database name                      | `dashboard`               |
| `POSTGRES_USER`          | Database user                      | `postgres`                |
| `POSTGRES_PASSWORD`      | Database password                  | `postgres`                |
| `POSTGRES_HOST`          | Database host                      | `localhost`               |
| `POSTGRES_PORT`          | Database port                      | `5432`                    |
| `GEMINI_API_KEY`         | Google Gemini API key              | -                         |
| `GEMINI_API_KEY`         | Google Gemini API key              | -                         |
| `TITILER_URL`            | TiTiler internal URL (for Django)  | `http://titiler`          |
| `TITILER_EXTERNAL_URL`   | TiTiler external URL (for browser) | `http://localhost:8080`   |
| `RASTER_FILE`            | Raster filename in /data volume    | `raster_web_mercator.tif` |
