import logging
from pathlib import Path

import yaml

from src.loader import DataLoader

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open("config.yaml", "r", encoding = 'utf-8') as f:
    config = yaml.safe_load(f)

loader = DataLoader(config)
loader.load_all()

base_layer = loader.base_layer

for nam, join_layer in loader.join_layers.items():
    
    ## --- 1. Join Reihennummer to join_layer ---
    reihe_name = config['reihennummer_name']
    layer_reihe_joined = (
        join_layer.sjoin_nearest(
            base_layer[[reihe_name, "geometry"]],
            how="left",
            max_distance=config['max_join_distance'],
            lsuffix=None,
            rsuffix="right",
        )
        .drop(columns=["index_right"])
        .copy()
    )
    layer_reihe_joined[reihe_name] = layer_reihe_joined[reihe_name].fillna(
        layer_reihe_joined[f"{reihe_name}_right"]
    )
    layer_reihe_joined.drop(columns=[f"{reihe_name}_right"], inplace = True)

    ## --- 2. Number Bäume/Säulen from south to north in join_layer ---
    entity_name = [i for i in [config['baumnummer_name'], config['säulennummer_name']] if i in layer_reihe_joined.columns][0]
    layer_reihe_joined['y_coord'] = layer_reihe_joined.geometry.y
    layer_reihe_joined[f"_{entity_name}"] = layer_reihe_joined.groupby('Reihe')['y_coord'].rank(method='first', ascending=True)
    layer_reihe_joined = layer_reihe_joined.drop(columns=['y_coord'])

    layer_reihe_joined[entity_name] = layer_reihe_joined[entity_name].fillna(
        layer_reihe_joined[f"_{entity_name}"]
    )
    layer_reihe_joined.drop(f"_{entity_name}", axis = 1, inplace = True)

    layer_nam = config['layers'][nam]['layer_name']
    out_path = config['out_data']
    if not Path(out_path).exists():
        layer_reihe_joined.to_file(out_path, layer=layer_nam, driver="GPKG")
        logger.info(f"Saved layer to {out_path} as {layer_nam}")
    elif config['overwrite']:
        layer_reihe_joined.to_file(out_path, layer=layer_nam, driver="GPKG")
        logger.info(f"Updated layer {layer_nam} in {out_path}")
    else:
        logger.info(f"{out_path} already exists but overwrite is set to false. Skipping layer writing")


