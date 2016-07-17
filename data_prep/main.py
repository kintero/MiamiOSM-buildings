import sys
from db_handler import DBHandler
from osm_handler import OSMHandler

def get_args():
    import argparse
    p = argparse.ArgumentParser(description="Data preparation for Miami's OSM Building import")
    p.add_argument('-setup', '--setup', help='Set up Postgres DB.', action='store_true')
    p.add_argument('-bd', '--buildings_download', help='Download Buildings from OSM', action='store_true')
    p.add_argument('-ad', '--address_download', help='Download Addresses from OSM', action='store_true')
    p.add_argument('-rd', '--roads_download', help='Download highway=* from OSM', action='store_true')
    p.add_argument('-b', '--bbox', help='BBOX for OSM download (min_lat, min_long, max_lat, max_long). Whole extent of Large buildings is used if left empty')
    p.add_argument('-f', '--fix', help='Fix PostGIS geometry errors', action='store_true')
    p.add_argument('-d', '--dsn', help='Dsn for database connection.')
    p.add_argument('-i', '--intersect', help='Performs intersection of Large Buildings and OSM buildings.', action="store_true")
    p.add_argument('-v', '--vacuum', help='Vacuums Postgres DB.', action="store_true")
    p.add_argument('-idx', '--index_data', help='Creates indexes on several tables.', action="store_true")
    p.add_argument('-a', '--assign_address', help='Assigns an address to buildings with only 1 overlapping address point.', action="store_true")
    return p.parse_args()

if __name__ == "__main__":
    args = vars(get_args())
    setup = args["setup"]
    building_download = args["buildings_download"]
    address_download = args["address_download"]
    fix = args["fix"]
    dsn = args["dsn"]
    intersect = args["intersect"]
    address = args["assign_address"]
    vacuum = args["vacuum"]
    index = args["index_data"]
    bbox = args["bbox"]

    db = DBHandler(dsn)
    osm = OSMHandler(bbox)

    if setup:
        print 'Setting up the database.'
        db.setup_db()

    if building_download:
        print 'Querying OverpassAPI for buildings.'
        buildings = osm.query_buildings()
        print 'Uploading OSM buildings to Postgres...'
        db.upload_osm(buildings, 'osm_buildings')

    if address_download:
        print 'Querying OverpassAPI for addresses.'
        addresses = osm.query_address()
        print 'Uploading OSM addresses to Postgres...'
        db.upload_osm(addresses, 'osm_address')

    if roads_download:
        print 'Querying OverpassAPI for highway=*.'
        roads = osm.query_roads()
        print 'Uploading OSM highway=* to Postgres...'
        db.upload_osm(roads, 'osm_highway_railway')

    if fix:
        print 'Fixing geometry errors in Large Buildings dataset.'
        db.fix_invalid_geom()

    if vacuum:
        print 'Updating DB stats.'
        db.update_stats()

    if index:
        print 'Creating multiple indexes.'
        db.create_index()

    if intersect:
        print 'Intersecting OSM buildings with Large buildings. Populating tables for overlapping and non-overlapping buildings.'
        db.do_intersection()

    if address:
        print 'Assigning addresses to buildings.'
        db.update_address()

    print 'Closing DB connection.'
    db.close_db_conn()
