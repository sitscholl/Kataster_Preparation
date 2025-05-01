from datetime import datetime
from collections import defaultdict


def create_naturamon_json(
    baum_data,
    parcel_id: int,
    parcel_name: str,
    reihennummer_name: str,
    baumnummer_name: str,
    pillars_data = None,
):
    """
    Script to transform GeoJSON tree data into a JSON structure suitable for database insertion in naturamon.
    The GeoJSON tree data needs to correspond to a point layer, where each point represents a tree and has the
    following two attributes: 'reihennummer_name' (row number) and 'baumnummer_name' (tree number).
    No coordinate transformation or checks are done, therefore make sure that the GeoJSON has the EPSG:4326 coordinate system,
    otherwise the output coordinates will not be suitable for database insertion.
    """

    # Group trees by row number
    trees_by_row = defaultdict(list)
    for feature in baum_data['features']:
        row_num = feature['properties'][reihennummer_name]
        trees_by_row[row_num].append(feature)

    # Initialize the result list with the parcel
    current_timestamp = int(datetime.now().timestamp() * 1000)
    created_date = datetime.now().strftime("%Y-%m-%dT")
    result = []

    # Add parcel (base object)
    base_id = parcel_id
    result.append({
        "ID": base_id,
        "Class": "parcel",
        "Number": 0,
        "ClassNumber": 1,
        "ParentID": None,
        "BaseID": None,
        "Name": parcel_name,
        "PrevObjDistance": 0.0,
        "Coordinates": None,
        "IsAnchor": 0,
        "Created": f"{created_date}T06:51:10",
        "LastModified": current_timestamp,
        "Deleted": 0
    })

    # Generate row and tree objects
    current_id = base_id + 1

    # First, create all rows
    for row_num in sorted(trees_by_row.keys()):
        result.append({
            "ID": current_id,
            "Class": "row",
            "Number": row_num,
            "ClassNumber": 0,
            "ParentID": base_id,
            "BaseID": base_id,
            "Name": None,
            "PrevObjDistance": 0.0,
            "Coordinates": None,
            "IsAnchor": 0,
            "Created": f"{created_date}T06:51:10",
            "LastModified": current_timestamp,
            "Deleted": 0
        })
        row_id = current_id
        current_id += 1

        # Add trees for this row
        for tree in sorted(trees_by_row[row_num], key=lambda x: x['properties'][baumnummer_name]):
            coords = tree['geometry']['coordinates']
            result.append({
                "ID": current_id,
                "Class": "tree",
                "Number": tree['properties'][baumnummer_name],
                "ClassNumber": tree['properties'][baumnummer_name],
                "ParentID": row_id,
                "BaseID": base_id,
                "Name": None,
                "PrevObjDistance": 0.0,
                "Coordinates": f"POINT({coords[0]} {coords[1]})",
                "IsAnchor": 1 if tree['properties'][baumnummer_name] == 1 else 0,
                "Created": f"{created_date}T06:51:10",
                "LastModified": current_timestamp,
                "Deleted": 0
            })
            current_id += 1

    return result


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
