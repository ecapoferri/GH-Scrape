import geopandas as gpd
from geopandas import GeoDataFrame as Gdf
from shapely.geometry import Polygon as Pg, Point
import pandas as pd
from pandas import DataFrame as Df
import numpy as np
from collections import namedtuple
from shapely.geometry import Point
from urllib.parse import urlencode, quote

# these used to be here, passing these func through to scripts
#    written prior to these  splitting off to their own module
from useful_func import\
    str_to_list,\
    input_y_default,\
    input_y_no_loopother,\
    input_y_otherfalse,\
    jsonextr


# named tuple for use in assigning a name 'tag' to a point if within a polygon
PgsTagPair = namedtuple('PgsTagPair', ('polyg', 'tag'))
"""Useful for assigning text value 'tag' to geographies that have any specific geometric comparison to 'polyg'"""
LatLngPair = namedtuple('LatLngPair', ('lng', 'lat'))


def query_url(api_url: str, args: dict, qmark: bool=True) -> str:
    """Assembles url with api parameters

    Args:
        api_url (str): api endpoint base url
            include reused parameters, set qmark to false to omit '?'
        args (dict): format pairs as <param>: <arg>
            use with your dynamic param/args
            use urllib.parse.quote to properly format strings as necessary
            before passing into this func
        qmark (bool, optional): Whether to include '?'. Defaults to True.

    Returns:
        str: full url encoded
    """
    q: str = '?' if qmark else ''
    f_args_str: str = urlencode(args)
    return f"{api_url}{q}{f_args_str}"


def ptstring_topoint(ptstr: str) -> Point:
    """
    Args:
        ptstr (str): string that has been converted from a shapely.geometry Point object

    Raises:
        Exception: general for any issues

    Returns:
        Point: shapely.geometry Point object
    """
    try:
        # 'POINT( ' 7 chars; ')' 1 char
        pS_list = ptstr[7:-1].split(" ")
        pF_list = [float(s) for s in pS_list]
        pt = Point(pF_list)
        return pt
    except ValueError:
        raise Exception(f"Something is wrong with the string passed to ptstring_topoint. " +\
            f"Maybe its not a shapely Point-like string.")

def latlng_to_geometry(df: Df) -> Df:
    """_summary_

    Args:
        df (pd.DataFrame): must have:
            'lat' with latitude
            'lng' with longitude

    Returns:
        pd.DataFrame: _description_
    """
    df['geometry'] = pd.NA

    df['geometry'] = [Point(p) for p in zip(df.lng, df.lat)]
    return df
    

def geom_to_latlng(gdf: Gdf) -> Gdf:
    """Creates a independent latitude and longitude value columns

    Args:
        gdf (gpd.GeoDataFrame): all geometry should be single Points

    Returns:
        gdf (gpd.GeoDataFram): with 'lat' column with latitude values
            and 'lng' column with longitude values
    """

    gdf['lng'] = gdf.geometry.apply(
            lambda p: float(p.x)
        )
    gdf['lat'] = gdf.geometry.apply(
            lambda p: float(p.y)
        )
    return gdf


def is_in(df: Df) -> Gdf:
    """Takes a dataframe arg containing geometry col;
        returns whether it is within service area or comp area,
        specific to this project, is_within is a more generalized version"""
    # gdf = gpd.GeoDataFrame(the_df, geometry=gpd.points_from_xy(the_df.lng, the_df.lat))
    gdf = Gdf(df)
    del df
    gdf.reset_index(inplace=True, drop=True)
    gdf['is_in'] = np.NaN
    # initialize empty column for is_in values

    ca_pg = gpd.read_file('scrape_files/comp_area_compound.geojson').unary_union
    sa_pg = gpd.read_file('scrape_files/service_area.geojson').unary_union

    caser = {(True,False):'ca',(False,True):'sa',(False,False):'outside',(True,True):'both?'}
    for row in gdf.itertuples():
        pt = row.geometry
        # print(f"{pt} is type {type(pt)}")
        tf = ( ca_pg.contains(pt), sa_pg.contains(pt) )
        gdf.loc[row.Index,'is_in'] = caser[tf]
        del pt, tf
    del ca_pg, sa_pg

    return gdf
    

def is_within_gdf(gdf: Gdf, pgs_tags_list: list) -> gpd.GeoDataFrame:
    """For a pandas dataframe or geopandas geodataframe, analyzes whether points are within exclusive polygons a list of
        and adds a corresponding tag for which.

    >>> from my_gis_etl_module.py import PgsTagPair

    Args:
        df (pd.DataFrame): dataframe containing a geometry column with shapeli.geometry.Point objects only
        pgs_tags_list (list[PgsTagPair]): list of namedtuples, classed in this module:
            PgsTagPair(polyg=<shapely.geometry.Polygon/Multipolygon>, tag=<string for corresponding tag>)


    Returns:
        gpd.GeoDataFrame: _description_
    """

    
    def is_within_eval(pt: Point) -> str:
        tag_strs: str = None

        for p in pgs_tags_list:
            if p.polyg.contains(pt):
                tag_strs = p.tag

        return tag_strs

    return gdf.assign(is_within=gdf.geometry.apply(lambda pt: is_within_eval(pt)))


def gdf_to_geojson(gdf: gpd.GeoDataFrame, fn_noext: str) -> None:
    try:
        gdf.to_file(f"{fn_noext}.geojson", driver='GeoJSON')
    except Exception:
        raise Exception("Something went wrong saving the file.")


def tag_count_compile(df: pd.DataFrame, tag_colname: str) -> pd.DataFrame:
    """Counts all occurrences of list elements, puts in a df"""

    # appends all lists together, built to deal lists or a list-like string
    biglist = []
    
    df[tag_colname].apply(
        lambda x: [ biglist.append(i) for i in str_to_list(x) ]
        )

    # counts distinct occurrences
    # get distinct tags by making a set from the list
    fullset = set(biglist)
    

    # a dict to store results for df'ing
    full_tab_dict = {}
    # compare each distinct tag to every tag and count matches,
    #  load as a kv into the dict
    for t in fullset:
        c = 0  # counter increments for a match
        for i in biglist:
            if t == i: c += 1 

        full_tab_dict[t] = c

    del i, c, t

    # resulting df has an index of every tag and a count of occurrences
    return pd.DataFrame.from_dict(full_tab_dict, orient='index')


# %%
# gdf definitions
# ===============

def read_in(fn: str) -> Gdf:
    return gpd.read_file(fn)


common_crs_str = 'EPSG:4326'

# load config data
config_args = jsonextr('my_gis_module-config.json')

# dict of local source paths
src_p: dict = config_args['local_geo_src']

# get standard name of row headings
rownamecol = config_args['standard_headings']['row_label']

nbh_gdf = read_in(src_p['nbh'])
service_area_gdf = read_in(src_p['service_area'])
water_gdf = read_in(src_p['water'])
# collar municipalities, mainly southside, within com area pseudo-isochrone
collarmun_sthsd_gdf = read_in(
    src_p['collarmun_sthsd']
)
# competition area definittion
# see 'iso_construct.ipynb' for comp_area construction
comp_area_gdf = read_in(src_p['comp_area'])
# TODO #6 RE-DEFINE COMP AREA TO HAVE SEPARATE FEATURES FOR COLLAR_MUNS AND NBHS
# JUST INTERSECT/OVERLAY WITH 
comp_area_pg: Pg = comp_area_gdf.unary_union

# restaurant locations
restLoc_gdf = read_in(src_p['restLoc'])
towns_gdf = read_in(src_p['chiland_muns'])

service_area_pg: Pg = service_area_gdf.unary_union

zips_sa_gdf = read_in(src_p['zips_sa'])
zips_ca_gdf = read_in(src_p['zips_ca'])

