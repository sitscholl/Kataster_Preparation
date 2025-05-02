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
loader.load_layer('gerüst')

for parcel_name, parcel_trees in loader.join_layers['bäume'].groupby(wiese_name):

    parcel_pillars = loader.join_layers['gerüst']
    parcel_pillars = parcel_pillars.loc[parcel_pillars[wiese_name] == parcel_name].dropna(subset = config['säulennummer_name'])

    if parcel_trees[config['reihennummer_name']].isna().any():
        logger.warning(f"Missing values in column {config['reihennummer_name']} for parcel {parcel_name}. Json generation is skipped")
        continue
    if parcel_trees[config['baumnummer_name']].isna().any():
        logger.warning(f"Missing values in column {config['baumnummer_name']} for parcel {parcel_name}. Json generation is skipped")
        continue

    naturamon_json = create_naturamon_json(
        parcel_trees,
        parcel_name,
        reihennummer_name = config['reihennummer_name'],
        baumnummer_name = config['baumnummer_name'],
        parcel_pillars = parcel_pillars,
        säulennummer_name=config['säulennummer_name']
    )

    # Save the result
    json_path = Path(config['naturamon']['out_data'], parcel_name + '.json')
    json_path.parent.mkdir(exist_ok=True, parents=True)
    with open(json_path, 'w') as f:
        json.dump(naturamon_json, f, indent=2)
    logger.info(f"Transformation completed. File saved as {json_path}")
    