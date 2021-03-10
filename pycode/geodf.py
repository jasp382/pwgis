"""
GeoDataFrame tools
"""


def geodf_to_gjson(gdf):
    """
    Convert GeoDataFrame to GeoJson
    """

    return gdf.to_json()


def featext_to_dfcols(df, geomCol):
    """
    Add minx, miny, maxx, maxy to dataframe
    """
    
    return df.merge(
        df[geomCol].bounds, how='inner',
        left_index=True, right_index=True
    )

