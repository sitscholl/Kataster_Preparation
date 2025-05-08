import numpy as np
import logging

import geopandas as gpd

from ..geometry_checks import convert_multipoint_to_point

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, in_data, config):
        self.in_data = in_data
        self.config = config
        self.base_layer = None
        self.join_layers = {}

    def validate(self, gdf, layer_type):
        """Validate the geodataframe."""
        if layer_type == 'base_layer' and not self.config['count_name'] in gdf.columns:
            raise ValueError(f"Column {self.config['count_name']} not found in base layer.")
        if layer_type == 'base_layer' and not self.config['wiesen_name'] in gdf.columns:
            raise ValueError(f"Column {self.config['wiesen_name']} not found in base layer.")

        if layer_type == 'join_layer' and not self.config['class_count_name'] in gdf.columns:
            raise ValueError(f"Column {self.config['class_count_name']} not found in join layer.")
        if layer_type == 'join_layer' and not self.config['parent_name'] in gdf.columns:
            raise ValueError(f"Column {self.config['parent_name']} not found in join layer.")

        if not self.config['class_name'] in gdf.columns:
            raise ValueError(f"Column {self.config['class_name']} not found in layer.")

    def load_layer(self, key):
        """Generic method to load a single layer."""
        layer_config = self.config['layers'][key]
        layer_name = layer_config['layer_name']
        layer_type = layer_config['type']

        gdf = gpd.read_file(self.in_data, layer=layer_name)
        self.validate(gdf, layer_type)

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
