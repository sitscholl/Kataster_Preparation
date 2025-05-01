import logging
from pathlib import Path
import json
import yaml

from src.loader import DataLoader
from src.naturamon import create_naturamon_json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open("config.yaml", "r", encoding = 'utf-8') as f:
    config = yaml.safe_load(f)
wiese_name = config['wiesen_name']

loader = DataLoader(in_data = config['naturamon']['in_data'], config = config)
loader.load_layer('bäume')
numbered_layer = loader.join_layers['bäume']

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
    json_path = Path(config['naturamon']['out_data'], parcel_name + '.json')
    json_path.parent.mkdir(exist_ok=True, parents=True)
    with open(json_path, 'w') as f:
        json.dump(naturamon_json, f, indent=2)
    logger.info(f"Transformation completed. File saved as {json_path}")

    parcel_id += 1
