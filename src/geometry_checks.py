import logging

from shapely.geometry import Point, MultiPoint
import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)

def convert_multipoint_to_point(gdf):
    """
    Convert MultiPoint geometries to Point geometries with validation checks.

    Parameters:
    -----------
    gdf : GeoDataFrame
        Input GeoDataFrame with MultiPoint geometries
    verbose : bool, default False
        If True, prints additional information during conversion

    Returns:
    --------
    GeoDataFrame
        A new GeoDataFrame with Point geometries

    Raises:
    -------
    ValueError
        If any geometry is not MultiPoint or if any MultiPoint contains multiple points
    TypeError
        If input is not a GeoDataFrame
    """
    # Type checking
    if not isinstance(gdf, gpd.GeoDataFrame):
        logger.error("Input must be a GeoDataFrame")
        raise TypeError("Input must be a GeoDataFrame")

    # Check if empty
    if gdf.empty:
        logger.error("Input GeoDataFrame is empty")
        raise ValueError("Input GeoDataFrame is empty")

    # Check for null geometries
    null_geoms = gdf[gdf.geometry.isna()]
    if not null_geoms.empty:
        logger.error(f"Found null geometries at indices: {null_geoms.index.tolist()}")
        raise ValueError(f"Found null geometries at indices: {null_geoms.index.tolist()}")

    # Check geometry types
    geom_types = gdf.geometry.geom_type.unique()
    if all(gt == 'Point' for gt in geom_types):
        logger.debug('All geometries are already of point class')
        return(gdf)

    if not all(gt == 'MultiPoint' for gt in geom_types):
        logger.error(f"All geometries must be MultiPoint. Found types: {geom_types}")
        raise ValueError(
            f"All geometries must be MultiPoint. Found types: {geom_types}"
        )

    # Check for MultiPoints with more than one point
    point_counts = gdf.geometry.apply(lambda x: len(x.geoms))
    multiple_points = gdf[point_counts > 1]

    if not multiple_points.empty:
        # Create detailed error message
        error_details = pd.DataFrame({
            'index': multiple_points.index,
            'point_count': point_counts[multiple_points.index],
            'coordinates': multiple_points.geometry.apply(lambda x: [list(p.coords) for p in x.geoms])
        })
        error_msg = (
            f"Found {len(multiple_points)} MultiPoint geometries with multiple points:\n"
            f"{error_details.to_string()}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Convert to Points
    gdf_new = gdf.copy()
    gdf_new.geometry = gdf_new.geometry.apply(
        lambda x: Point(x.geoms[0].x, x.geoms[0].y)
    )

    logger.info(f"All {len(gdf_new)} geometries converted to Point type")

    return gdf_new