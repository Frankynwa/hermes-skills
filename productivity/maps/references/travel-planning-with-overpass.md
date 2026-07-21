# Travel Planning with Overpass API

Pattern for building a walking itinerary from raw POI data when `maps_client.py` is unavailable.

## Step 1: Geocode the starting point

Use known coordinates or estimate from city/district/street name.
For Chinese addresses, OSM coverage varies — major cities are well-mapped,
smaller cities may need manual coordinate lookup.

## Step 2: Query POIs with Overpass API

```bash
curl -s --connect-timeout 10 --max-time 30 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'data=[out:json][timeout:30];(
    node["amenity"~"cafe|restaurant|marketplace|fast_food"](S,W,N,E);
    node["leisure"~"park|garden|fitness_centre"](S,W,N,E);
    way["leisure"~"park|garden"](S,W,N,E);
    node["tourism"~"attraction|museum|viewpoint|artwork"](S,W,N,E);
  );out center body 50;' \
  "https://overpass-api.de/api/interpreter"
```

Bounding box: `(south, west, north, east)` in decimal degrees.
- 2km radius from center ≈ ±0.018° lat, ±0.025° lon (varies by latitude)
- At 43°N (Urumqi): 1° lat ≈ 111km, 1° lon ≈ 81km

## Step 3: Calculate distances and walking times

```python
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

home = (lat, lon)  # Starting point
# Walking speed: ~80m/min (flat), ~60m/min (hilly), ~100m/min (fast)
walk_min = distance_m / 80
```

## Step 4: Sort by distance and build route

Sort POIs by distance from starting point, then chain them into a
walking route. For 2-3 hour morning walks, aim for 4-6km total distance.

## Step 5: Format output

- Each stop: name, distance, walking time, Google Maps link
- Time table with activities per stop
- Tips (weather, timezone, local customs)

Google Maps link format:
```
https://www.google.com/maps/search/?api=1&query={lat},{lon}
```

## Overpass API Tag Reference (common)

| Category | Key | Values |
|----------|-----|--------|
| Food/Drink | amenity | restaurant, cafe, fast_food, bar, marketplace |
| Parks | leisure | park, garden, fitness_centre |
| Tourism | tourism | attraction, museum, viewpoint, artwork, information |
| Shopping | shop | supermarket, convenience, bakery |
| Transport | amenity | bus_station, taxi |
| Religious | amenity | place_of_worship |

## Chinese city time zones to know

- **Xinjiang (乌鲁木齐 etc.)**: UTC+6 local time, but businesses often use
  Beijing time (UTC+8). Sunrise ~6:50 Xinjiang time in summer.
  Ask locals which time a business uses.
- **Rest of China**: UTC+8 (Beijing time) universally.
