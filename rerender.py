import ast

import pandas as pd
import folium

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

def render_and_save_map():
    article_loc_map = runner.run_and_get_geolocs()
    df = map_to_df_locs(article_loc_map)
    f_map = folium.Map()
    df['Coords'] = df['Coords'].apply(ast.literal_eval)
    df.apply(lambda row: folium.CircleMarker(location=row['Coords'], radius=10, popup=row['Geoloc'])
             .add_to(f_map), axis=1)
    f_map.save("templates/render.html")






if __name__ == '__main__':
    render_and_save_map()