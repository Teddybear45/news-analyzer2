def __get_geoloc_coords(gpe, geocode):
    loc = geocode(gpe)

    if loc is not None:
        return (loc.latitude, loc.longitude)
    else:
        return None
def get_locations(locations, geocode):
    located_gpes = []
    for location in locations:
        got_loc = __get_geoloc_coords(location, geocode)
        if got_loc:
            located_gpes.append((location, got_loc))

    return located_gpes