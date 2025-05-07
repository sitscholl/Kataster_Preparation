import geopandas as gpd

from ..geometry_checks import convert_multipoint_to_point

def load_layer(source, layer, layer_type):
    gdf = gpd.read_file(source, layer=layer)
    gdf = convert_multipoint_to_point(gdf)

    if layer_type.lower() == 'gerüst':
        gdf = gdf.loc[gdf['Typ'].isin(['Säule', 'Ortssäule'])].copy()
        gdf.rename(columns = {'Säule': 'ClassNumber', 'Reihe': 'ParentID'}, inplace = True)
        gdf['ClassName'] = 'pillar'
    elif layer_type.lower() == 'bäume':
        gdf.rename(columns = {'Baum': 'ClassNumber', 'Reihe': 'ParentID'}, inplace = True)
        gdf['ClassName'] = 'tree'
    else:
        raise ValueError(f'Unknown layer_type {layer_type}')

    return gdf