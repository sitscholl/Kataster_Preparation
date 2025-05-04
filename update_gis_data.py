import logging
from pathlib import Path

import yaml

from src.loader import DataLoader
from src.utils import join_with_base_layer, number_entities

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open("config.yaml", "r", encoding = 'utf-8') as f:
    config = yaml.safe_load(f)

loader = DataLoader(in_data = config['in_data'], config = config)
loader.load_all()

base_layer = loader.base_layer

for nam, join_layer in loader.join_layers.items():

    ## --- 1. Join Reihennummer to join_layer ---
    reihe_name = config['reihennummer_name']
    wiese_name = config['wiesen_name']
    joined_layer = join_with_base_layer(
        join_layer,
        base_layer,
        wiese_name,
        reihe_name,
        config["max_join_distance"],
    )
    logging.info(f"Added numbering to {reihe_name} in {nam}")

    ## --- 2. Number Bäume/Säulen from south to north in join_layer ---
    entity_name = [i for i in [config['baumnummer_name'], config['säulennummer_name']] if i in joined_layer.columns][0]
    numbered_layer = number_entities(joined_layer, entity_name, group_by_column = [wiese_name, reihe_name])
    logging.info(f"Numbered {entity_name} in {nam}")

    layer_nam = config['layers'][nam]['layer_name']
    out_path = config['out_data']
    if not Path(out_path).exists():
        numbered_layer.to_file(out_path, layer=layer_nam, driver="GPKG")
        logger.info(f"Saved layer to {out_path} as {layer_nam}")
    elif config['overwrite']:
        numbered_layer.to_file(out_path, layer=layer_nam, driver="GPKG")
        logger.info(f"Updated layer {layer_nam} in {out_path}")
    else:
        logger.info(f"{out_path} already exists but overwrite is set to false. Skipping layer writing")
