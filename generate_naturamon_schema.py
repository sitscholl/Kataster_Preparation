import logging
from pathlib import Path
import json

import pandas as pd
import numpy as np
import yaml

from src.naturamon.model import create_naturamon_json
from src.naturamon.data import load_layer
from src.utils import number_entities

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

with open("config.yaml", "r", encoding = 'utf-8') as f:
    config = yaml.safe_load(f)
wiese_name = config['wiesen_name']

gdf_bäume = load_layer(config['naturamon']['in_data'], layer = config['naturamon']['bäume_layer'], layer_type = 'bäume')
gdf_gerüst = load_layer(config['naturamon']['in_data'], layer = config['naturamon']['gerüst_layer'], layer_type='gerüst')
gdf = pd.concat([gdf_bäume, gdf_gerüst]).dropna(subset = "Wiese")

gdf['Number'] = np.nan
numbered_gdf = number_entities(gdf, 'Number', ['Wiese', 'ParentID'])

for parcel_name, entities in numbered_gdf.groupby(wiese_name):

    missing_vals = False
    for col in ['ParentID', 'Number', 'ClassNumber']:
        if entities[col].isna().any():
            logger.warning(f"Missing values in column {col} for parcel {parcel_name}. Json generation is skipped")
            missing_vals = True
            break

    if missing_vals:
        continue

    naturamon_json = create_naturamon_json(
        entities,
        parcel_name,
    )

    # Save the result
    json_path = Path(config['naturamon']['out_data'], parcel_name + '.json')
    json_path.parent.mkdir(exist_ok=True, parents=True)
    with open(json_path, 'w') as f:
        json.dump(naturamon_json, f, indent=2)
    logger.info(f"Transformation completed. File saved as {json_path}")
    