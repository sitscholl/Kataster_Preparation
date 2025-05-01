import logging
from pathlib import Path
import json

import yaml

from src.loader import DataLoader
from src.utils import join_with_base_layer, number_entities
from src.naturamon import create_naturamon_json

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

    if config['save_naturamon_json'] and nam.lower() == 'bäume':
        parcel_id = 1
        for parcel_name, parcel_baume in numbered_layer.groupby(wiese_name):

            if parcel_baume[config['reihennummer_name']].isna().any():
                logger.warning(f"Missing values in column {config['reihennummer_name']} for parcel {parcel_name}. Json generation is skipped")
                continue
            if parcel_baume[config['baumnummer_name']].isna().any():
                logger.warning(f"Missing values in column {config['baumnummer_name']} for parcel {parcel_name}. Json generation is skipped")
                continue

            geojson_data = json.loads(parcel_baume.to_json(
                to_wgs84=True,  # converts to WGS84 CRS
                drop_id=True    # don't include the index as an id property
            ))

            naturamon_json = create_naturamon_json(
                geojson_data,
                parcel_id,
                parcel_name,
                reihennummer_name = config['reihennummer_name'],
                baumnummer_name = config['baumnummer_name'],
            )

            # Save the result
            json_path = Path(config['out_naturamon'], parcel_name + '.json')
            json_path.parent.mkdir(exist_ok=True, parents=True)
            with open(json_path, 'w') as f:
                json.dump(naturamon_json, f, indent=2)
            logger.info(f"Transformation completed. File saved as {json_path}")

            parcel_id += 1
