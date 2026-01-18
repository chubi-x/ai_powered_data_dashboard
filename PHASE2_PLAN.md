# Phase 2: Frontend Development - Detailed Lego-Style Plan

## Current Status Recap

**Phase 1 (API Layer) - Complete ✅**
- ✅ Three API endpoints: `/api/regions/`, `/api/modules/`, `/api/projections/`
- ✅ UUID field added to models for secure external references
- ✅ 25 comprehensive unit tests
- ✅ Updated README and dependencies
- ✅ Committed and PR created (#4)

**Phase 2 Goals:**
- Server-rendered Django templates with HTMX for interactivity
- Plotly.js for charts, Leaflet for maps
- Tailwind CSS for styling
- Headline stats (aggregate data cards, filterable by year/item)
- Tabbed interface for modules with chart placeholders
- 65:35 layout split (map:charts)

---

## Lego-Style Implementation Plan

### Chunk 1: Model Refactoring (10-15 min)
**Goal:** Consolidate duplicated `VariableChoices` into `BaseProjection` and prepare for aggregate queries.

**Tasks:**
- Move `VariableChoices` class from concrete models to `BaseProjection`
- Update concrete models to inherit `VariableChoices` from base
- Create migration for the refactoring
- Add database indexes if needed for aggregation performance

**Deliverable:** Clean model hierarchy with shared `VariableChoices`

### Chunk 2: django-tailwind Setup (15-20 min)
**Goal:** Get Tailwind CSS integrated with hot-reloading for rapid frontend development.

**Tasks:**
- Install `django-tailwind` and dependencies
- Run `python manage.py tailwind init` (standalone mode, no Node.js)
- Configure `TAILWIND_APP_NAME` in settings
- Add `django_browser_reload` for hot-reloading in DEBUG mode
- Create basic theme app structure

**Deliverable:** `python manage.py tailwind dev` command working with hot-reload

### Chunk 3: Headline Stats API Endpoint (20-25 min)
**Goal:** Create `/api/headline-stats/` endpoint that aggregates data across all modules.

**Tasks:**
- Add `headline_stats` function to `api_views.py`
- Implement aggregation logic: `SUM(value)` grouped by `variable`
- Add filters for `year` and `item` parameters
- Return JSON with totals for each variable type
- Add validation and error handling

**Deliverable:** Working API endpoint returning aggregate data

### Chunk 4: Base Template with Tailwind (15-20 min)
**Goal:** Create the main dashboard template with Tailwind layout structure.

**Tasks:**
- Create `templates/dashboard/base.html` with Tailwind CDN/include
- Set up basic layout: header, main content area
- Add 65:35 grid layout (map left, content right)
- Include HTMX for AJAX interactions
- Add Plotly.js and Leaflet.js script includes

**Deliverable:** Basic HTML structure with responsive layout

### Chunk 5: Headline Stats Cards (20-25 min)
**Goal:** Implement filterable headline stats cards in the template.

**Tasks:**
- Create Django view for main dashboard page
- Add year and item filter dropdowns (populate from API)
- Create HTMX endpoints for dynamic stat updates
- Design stat cards with Tailwind styling
- Add placeholder chart containers (Plotly.js will populate later)

**Deliverable:** Interactive stats cards that update via AJAX

### Chunk 6: Leaflet Map Placeholder (15-20 min)
**Goal:** Add basic Leaflet map in the 65% section.

**Tasks:**
- Initialize Leaflet map with OpenStreetMap tiles
- Set initial view (centered on Europe)
- Add basic map controls (zoom, layers)
- Style with Tailwind classes
- Prepare for future raster tile integration

**Deliverable:** Functional Leaflet map displaying base tiles

### Chunk 7: Tabbed Module Interface (20-25 min)
**Goal:** Create tabbed navigation for each module.

**Tasks:**
- Implement Tailwind-based tab component
- Add tabs for: Crop, Animal, Bioenergy, Land Cover
- Create placeholder content areas for each tab
- Add filter controls (region, item, variable) per tab
- Prepare structure for multiple charts per tab

**Deliverable:** Tabbed interface with filter controls (no charts yet)

### Chunk 8: Plotly.js Chart Placeholders (15-20 min)
**Goal:** Add basic Plotly chart containers that can be populated later.

**Tasks:**
- Create placeholder divs in each tab for charts
- Add JavaScript functions to render Plotly charts
- Connect to projections API for data fetching
- Implement basic time-series chart template
- Add loading states and error handling

**Deliverable:** Chart containers that can display data from API

### Chunk 9: Interactivity Integration (20-25 min)
**Goal:** Connect filters to API calls and update charts dynamically.

**Tasks:**
- Implement HTMX for filter dropdown changes
- Add JavaScript to fetch data from `/api/projections/`
- Update charts when filters change
- Add loading indicators and error states
- Test end-to-end: filter → API → chart update

**Deliverable:** Fully interactive dashboard with working filters

### Chunk 10: Polish & Testing (15-20 min)
**Goal:** Final touches and validation.

**Tasks:**
- Test all interactions work correctly
- Ensure responsive layout (desktop only)
- Add basic error handling for API failures
- Clean up any unused code
- Document any remaining TODOs

**Deliverable:** Production-ready Phase 2 frontend

---

## Total Estimated Time: 3-4 hours
## Dependencies: Plotly.js, Leaflet.js (already included), django-tailwind (new)

## Questions for Clarification

1. **Headline Stats Aggregation:** Should the aggregates be across ALL modules combined, or separate per module? The current request says "across all modules" but I want to confirm.

2. **Filter Logic:** For headline stats, filtering by `item` - since items are module-specific (e.g., "wht" is crop-specific), should we allow filtering by item across all modules, or restrict to items within the same module?

3. **Chart Types:** For the module tabs, should I start with basic time-series line charts, or do you have specific chart types in mind (bar, scatter, etc.)?

4. **Data Units:** The headline stats show aggregates - should we display them in their original units (ha, t, t/ha) or normalize them somehow?

Does this lego plan align with your vision? Ready to start with Chunk 1? 🚀