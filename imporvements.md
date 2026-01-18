- optimise queries. could probably make a queryset union in index page where 4 queries are made serially
- dont use cdns. bundle your own versions

* mobile responsive layout

* add more charts,
* dont swap out entire charts. maybe use js to build charts and do client side filtering
* don't make double requests when changing filters
* unit tests
* error logging
* rename "variable"" to match metric
* data governance. use private cloud hosted llm like with civo so proprietary data is not used to train public llms
* raster url still exposes raster location in the server. should obscure this even more by hooking into leaflet
