from datetime import datetime
from collections import defaultdict
import json
from geopandas import GeoDataFrame
from typing import ClassVar
from pydantic import BaseModel

class Entity(BaseModel):
    _counter: ClassVar[int] = 0  # Class variable to keep track of IDs

    ID: int
    Class: str
    Number: int
    ClassNumber: int
    ParentID: int | None
    BaseID: int | None
    Name: str | None = None
    PrevObjDistance: float = 0.0
    Coordinates: str | None = None
    IsAnchor: int = 0
    Created: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    LastModified: float = int(datetime.now().timestamp() * 1000)
    Deleted: int = 0

    _rows: dict = defaultdict(list)

    def __init__(self, **data):
        Entity._counter += 1  # Increment the counter
        if 'ID' not in data:  # Only set id if not provided
            data['ID'] = Entity._counter
        super().__init__(**data)

    @classmethod
    def reset_counter(self):
        Entity._counter = 0

    def add_row(self, row_num):
        self._rows[row_num].append(
            Entity(
                Class="row",
                Number=row_num,
                ClassNumber=0,
                ParentID=self.ID,
                BaseID=self.ID,
            )
        )

    def add_points(self, points, row_num, class_name = "Class", number_name = "Number", class_number_name = "ClassNumber"):
        if row_num not in self._rows.keys():
            raise ValueError("Row number not found in _rows. Initialize row first before adding trees.")

        row_id = self._rows[row_num][0].ID
        for feature in points:
            coords = feature['geometry']['coordinates']
            self._rows[row_num].append(
                Entity(
                    Class=feature['properties'][class_name],
                    Number=feature['properties'][number_name],
                    ClassNumber=feature['properties'][class_number_name],
                    ParentID=row_id,
                    BaseID=self.ID,
                    Coordinates=f"POINT({coords[0]} {coords[1]})",
                    IsAnchor=1 if feature['properties'][number_name] == 1 else 0
                )
            )

    def get_row(self, row_num):
        if row_num not in self._rows.keys():
            raise ValueError("Row number not found in _rows. Initialize row first.")

        row = self._rows[row_num]
        n_trees = len([i for i in row if i.Class == 'tree'])
        n_pillars = len([i for i in row if i.Class == 'pillar'])

        print(f"Row {row_num} has {n_trees} trees and {n_pillars} pillars")

    def print_overview(self):
        for row_num in self._rows.keys():
            self.get_row(row_num)

    def to_json(self):
        result = []
        result.append(self.model_dump())
        for row_num in self._rows.keys():
            result.extend([i.model_dump() for i in self._rows[row_num]])
        return(result)

def _group_by_row(json, entryname):
    data_by_row = defaultdict(list)
    for feature in json['features']:
        row_num = feature['properties'][entryname]
        data_by_row[row_num].append(feature)
    return data_by_row

def _to_json(gdf):
    return json.loads(gdf.to_json(
        to_wgs84=True,  # converts to WGS84 CRS
        drop_id=True    # don't include the index as an id property
    ))

def create_naturamon_json(
    entities: GeoDataFrame,
    parcel_name: str,
    config: dict[str, str]
    ):
    """
    Script to transform GeoJSON tree data into a JSON structure suitable for database insertion in naturamon.
    The GeoJSON tree data needs to correspond to a point layer, where each point represents a tree and has the
    following two attributes: 'reihennummer_name' (row number) and 'baumnummer_name' (tree number).
    No coordinate transformation or checks are done, therefore make sure that the GeoJSON has the EPSG:4326 coordinate system,
    otherwise the output coordinates will not be suitable for database insertion.
    """

    entities_json = _to_json(entities)

    # Group entities by row number
    trees_by_row = _group_by_row(entities_json, "ParentID")

    # Initialize Parcel
    Entity.reset_counter()
    parcel = Entity(
        ID=1,
        Class="parcel",
        Number=0,
        ClassNumber=1,
        ParentID=None,
        BaseID=None,
        Name=parcel_name,
    )

    for row_num in sorted(trees_by_row.keys()):
        # Add rows
        parcel.add_row(row_num)

        # Add trees/pillars to row
        parcel.add_points(
            sorted(trees_by_row[row_num], key=lambda x: x['properties'][config['count_name']]),
            row_num = row_num
            )

    return parcel.to_json()


# # Save the result
# with open('transformed_dietl_baume.json', 'w') as f:
#     json.dump(result, f, indent=2)

# print("Transformation completed. File saved as 'transformed_dietl_baume.json'")

# # Print some statistics
# print(f"\nStatistics:")
# print(f"Total number of rows: {len(trees_by_row)}")
# print(f"Total number of trees: {sum(len(trees) for trees in trees_by_row.values())}")
# print(f"Total number of objects created: {len(result)}")

# # Print first few objects as sample
# print("\nSample of the first few objects:")
# for obj in result[:3]:
#     print(json.dumps(obj, indent=2))
