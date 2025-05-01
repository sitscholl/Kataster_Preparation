import numpy as np
import logging

import geopandas as gpd

from .geometry_checks import convert_multipoint_to_point

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, config):
        self.config = config
        self.base_layer = None
        self.join_layers = {}

    def _add_missing_columns(self, gdf, required_columns, layer_name):
        """Add missing columns to the GeoDataFrame with NaN values."""
        for column_config_key in required_columns:
            column_name = self.config[column_config_key]
            if column_name not in gdf:
                gdf[column_name] = np.nan
                logger.info(f'Added column {column_name} to {layer_name}')
        return gdf

    def load_layer(self, key):
        """Generic method to load a single layer."""
        layer_config = self.config['layers'][key]
        layer_name = layer_config['layer_name']
        layer_type = layer_config['type']

        gdf = gpd.read_file(self.config['in_data'], layer=layer_name)
        gdf = self._add_missing_columns(
            gdf,
            layer_config['required_columns'],
            layer_name
        )
        if layer_type != 'base_layer': #the base_layer should be of type line, so skip this
            gdf = convert_multipoint_to_point(gdf)

        if layer_type == 'base_layer':
            if self.base_layer:
                raise ValueError('Base layer already exists. There can only be one base layer. Check configuration.')
            self.base_layer = gdf
        elif layer_type == 'join_layer':
            self.join_layers[key] = gdf
        else:
            raise ValueError(f'Unknown layer type: {layer_type}')

        logger.info(f'Loaded layer {layer_name} as {layer_type}')

    def load_all(self):
        """Load all layers."""
        for layer_key in self.config['layers'].keys():
            self.load_layer(layer_key)
