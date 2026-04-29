# adsb-flightalert 0.6
# parse a running dump1090/readsb install's aircraft.json for particular criteria in a key
# for example squawk = 7700 (or a range), flight = "blah", etc

def normalize_aircraft(aircraft):
    """
    Normalize/fix aircraft data without mutating input.
    """
    return {
        "hex": aircraft.get("hex"),
        "flight": (aircraft.get("flight") or "no callsign").strip(),
        "squawk": aircraft.get("squawk"),
        "lat": aircraft.get("lat"),
        "lon": aircraft.get("lon"),
        "raw": aircraft 
    }


def is_inside_box(coords_box, aircraft):
    """
    coords_box = [(lat1, lon1), (lat2, lon2)]
    """
    if aircraft["lat"] is None or aircraft["lon"] is None:
        return False

    y1, x1 = coords_box[0]
    y2, x2 = coords_box[1]

    min_x, max_x = sorted([x1, x2])
    min_y, max_y = sorted([y1, y2])

    return (min_x < aircraft["lon"] < max_x) and (min_y < aircraft["lat"] < max_y)


def match_filter(aircraft, filter_type, filter_value):
    if filter_type == "area":
        return is_inside_box(filter_value, aircraft)

    if filter_type == "squawk_range":
        squawk = aircraft["squawk"]
        if not squawk:
            return False

        try:
            sq = int(squawk)
            min_sq, max_sq = map(int, filter_value.split("-"))
            return min_sq <= sq <= max_sq
        except Exception:
            return False

    value = aircraft.get(filter_type)

    if value is None:
        return False

    return str(filter_value) in str(value)


def filter_aircraft(data, filters):
    """
    data = full aircraft.json
    filters = [("type", "value"), ...]

    Returns:
    [
        {
            "aircraft": {...},
            "matches": [(type, value), ...]
        }
    ]
    """
    results = []

    for raw in data.get("aircraft", []):
        aircraft = normalize_aircraft(raw)

        matches = []

        for ftype, fval in filters:
            if match_filter(aircraft, ftype, fval):
                matches.append((ftype, fval))

        if matches:
            results.append({
                "aircraft": aircraft,
                "matches": matches
            })

    return results
