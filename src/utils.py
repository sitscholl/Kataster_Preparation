import geopandas as gpd

def join_with_base_layer(join_layer, base_layer, wiesen_name, reihe_name, max_distance):
    """Join row number and field name of the base layer to the join layer based on spatial proximity."""
    joined_layer = (
        join_layer.sjoin_nearest(
            base_layer[[wiesen_name, reihe_name, "geometry"]],
            how="left",
            max_distance=max_distance,
            lsuffix=None,
            rsuffix="right",
        )
        .drop(columns=["index_right"])
        .copy()
    )
    joined_layer[reihe_name] = joined_layer[reihe_name].fillna(
        joined_layer[f"{reihe_name}_right"]
    )
    joined_layer.drop(columns=[f"{reihe_name}_right"], inplace = True)
    return joined_layer

def number_entities(layer, entity_name, group_by_column):
    """Number entities from south to north within each group."""
    numbered_layer = layer.copy()
    numbered_layer['y_coord'] = numbered_layer.geometry.y
    numbered_layer[f"_{entity_name}"] = numbered_layer.groupby(group_by_column)['y_coord'].rank(method='first', ascending=True)
    numbered_layer = numbered_layer.drop(columns=['y_coord'])

    numbered_layer[entity_name] = numbered_layer[entity_name].fillna(
        numbered_layer[f"_{entity_name}"]
    )
    numbered_layer.drop(f"_{entity_name}", axis = 1, inplace = True)
    return numbered_layer