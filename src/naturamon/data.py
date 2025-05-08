import geopandas as gpd

from ..geometry_checks import convert_multipoint_to_point

def load_layer(source, layer, layer_type, config):
    gdf = gpd.read_file(source, layer=layer)
    gdf = convert_multipoint_to_point(gdf)

    if layer_type.lower() == 'gerüst':
        gdf = gdf.loc[gdf[config['class_name']].isin(['Säule', 'Ortssäule'])].copy()
        gdf[config['class_name']] = 'pillar'
    elif layer_type.lower() == 'bäume':
        gdf[config['class_name']] = 'tree'
    else:
        raise ValueError(f'Unknown layer_type {layer_type}')

    return gdf