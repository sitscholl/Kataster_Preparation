import logging
from pathlib import Path

import yaml

from src.gis.loader import DataLoader
from src.utils import join_with_base_layer, number_entities

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

with open("config.yaml", "r", encoding = 'utf-8') as f:
    config = yaml.safe_load(f)

loader = DataLoader(in_data = config['in_data'], config = config)
loader.load_all()

base_layer = loader.base_layer

for nam, join_layer in loader.join_layers.items():
    logger.info(f"Processing layer {nam}")

    ## --- 1. Join Reihennummer to join_layer ---
    reihennummer_name = config['count_name']
    wiese_name = config['wiesen_name']
    parent_name = config['parent_name']
    joined_layer = join_with_base_layer(
        join_layer,
        base_layer,
        wiese_name,
        reihennummer_name,
        parent_name,
        config["max_join_distance"],
    )

    ## --- 2. Number Bäume/Säulen from south to north in join_layer ---
    numbered_layer = number_entities(
        joined_layer,
        config["class_count_name"],
        group_by_column=[wiese_name, parent_name],
        class_column = config['class_name']
    )

    ## --- 3. Save output ---
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
