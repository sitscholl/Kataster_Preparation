import logging

import numpy as np

logger = logging.getLogger(__name__)

def join_with_base_layer(join_layer, base_layer, wiesen_name, reihennummer_name, parent_name, max_distance):
    """Join row number and field name of the base layer to the join layer based on spatial proximity."""
    if not parent_name in join_layer.columns:
        join_layer[parent_name] = np.nan
        logger.warning(f"Added column {parent_name} to layer")
    if reihennummer_name in join_layer.columns:
        raise ValueError(f"Column {reihennummer_name} already exists in join layer.")

    joined_layer = (
        join_layer.sjoin_nearest(
            base_layer[[wiesen_name, reihennummer_name, "geometry"]],
            how="left",
            max_distance=max_distance,
            lsuffix=None,
            rsuffix="right",
        )
        .drop(columns=["index_right"])
        .copy()
    )
    joined_layer[parent_name] = joined_layer[parent_name].fillna(
        joined_layer[reihennummer_name]
    )
    joined_layer.drop(columns=[reihennummer_name], inplace = True)

    logger.info(f"Added parent ID in column {parent_name}")

    return joined_layer

def number_entities(layer, entity_name, group_by_column):
    """Number entities from south to north within each group."""

    numbered_layer = layer.copy()
    if not entity_name in layer.columns:
        layer[entity_name] = np.nan
        logger.warning(f"Added column {entity_name} to layer")

    numbered_layer['y_coord'] = numbered_layer.geometry.y
    numbered_layer[f"_{entity_name}"] = numbered_layer.groupby(group_by_column)['y_coord'].rank(method='first', ascending=True)
    numbered_layer = numbered_layer.drop(columns=['y_coord'])

    numbered_layer[entity_name] = numbered_layer[entity_name].fillna(
        numbered_layer[f"_{entity_name}"]
    )
    numbered_layer.drop(f"_{entity_name}", axis = 1, inplace = True)

    logger.info(f"Numbered entities in column {entity_name}")

    return numbered_layer