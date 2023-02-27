import ast

import pandas as pd
import folium
from folium.plugins import HeatMap
import folium.plugins as plugins

from analysis_scripts import runner

def map_to_df_locs(loc_map):
    data = []
    for url in loc_map.keys():
        for loc_tup in loc_map[url]:
            geoloc = loc_tup[0]
            coords = str(loc_tup[1])
            data.append([coords, geoloc, url])

    df = pd.DataFrame(data, columns=['Coords', 'Geoloc', 'Url'])
    return df

def render_and_save_map(article_loc_map):
    df = map_to_df_locs(article_loc_map)
    f_map = folium.Map()
    df['Coords'] = df['Coords'].apply(ast.literal_eval)
    df.apply(lambda row: folium.CircleMarker(location=row['Coords'], radius=10, popup=row['Geoloc'])
             .add_to(f_map), axis=1)

    coords_map = [list(x) for x in df['Coords'].tolist()]
    print(coords_map)

    hm = HeatMap(coords_map, gradient={0.1: 'blue', 0.3: 'lime', 0.5: 'yellow', 0.7: 'orange', 1: 'red'},
                 min_opacity=0.05,
                 max_opacity=0.9,
                 radius=25,
                 use_local_extrema=False).add_to(f_map)

    f_map.save("templates/renderAll.html")






if __name__ == '__main__':
    article_loc_map = runner.run_and_get_geolocs()
    render_and_save_map(article_loc_map)