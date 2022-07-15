###==================================================================================================================================================
###     BC Hydro Outages
###     (BCHydro_Outages.py)
###
###     Written by: Paulina Marczak and Michael Dykes
###
###     Created: May 27 2021
###     Edited: July 27 2021 (MDykes)
###
###     Purpose: Scrape BC Hydro Web Content (from https://www.bchydro.com/power-outages/app/outage-map.html) to ArcGIS Online Hosted Feature Layer
###==================================================================================================================================================
# Import libraries/modules
import requests, getpass
from arcgis.gis import GIS
from arcgis import geometry, features
from datetime import datetime, timezone

# Connect to BC GeoHub
PORTAL_URL = "https://Portal.arcgis.com"
PORTAL_USERNAME = "Username"
PORTAL_PASSWORD = getpass.getpass(prompt='Password: ')
gis = GIS(PORTAL_URL,PORTAL_USERNAME,PORTAL_PASSWORD)

# Get Hosted Feature Layer to Update
# HFS_item = gis.content.get("Item_ID")

# Request data from bchydro.com outages map
url = r"https://www.bchydro.com/power-outages/app/outages-map-data.json"
x = requests.get(url)

# If good web return
if x.status_code == 200:
    if x and x.json():
        # Delete all existing feature layer features and reset OBJECTID/FID counter

        # Iterate through bchydro JSON items (each outage is its own item)
        for row in x.json():
            print("ROW", row)
            # Build LAT/LONG list pairings from unseparated list of LAT/LONGS from website JSON
            latlong_list = [list(a) for a in zip(row["polygon"][::2],row["polygon"][1::2])]
            # Create Polygon Geometry WKID:4326 = WGS 1984
            geom = geometry.Geometry({"type": "Polygon", "rings" : [latlong_list],"spatialReference" : {"wkid" : 4326}})
            # Build attributes to populate feature attribute table, check for none values in the EST_TIME_ON, OFFTIME and UPDATED date fields
            attributes = {"OUTAGE_ID":row['id'], 
                    "GIS_ID":row['gisId'],
                    "REGION_ID": row['regionId'],
                    "REGION": row['regionName'],
                    "MUNI": row['municipality'],
                    "DETAILS": row['area'],
                    "CAUSE": row['cause'],
                    "AFFECTED":  row['numCustomersOut'],
                    "CREW_STATUS": row['crewStatusDescription'],
                    "EST_TIME_ON": datetime.utcfromtimestamp(row['dateOn']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['dateOn'] else None,
                    "OFFTIME": datetime.utcfromtimestamp(row['dateOff']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['dateOff'] else None,
                    "UPDATED": datetime.utcfromtimestamp(row['lastUpdated']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['lastUpdated'] else None,
                    "CREW_ETA": datetime.utcfromtimestamp(row['crewEta']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['crewEta'] else None,
                    "CREW_ETR": datetime.utcfromtimestamp(row['crewEtr']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['crewEtr'] else None,
                    "SHOW_ETA": row['showEta'],
                    "SHOW_ETR": row['showEtr']}
            # # Create new feature
            newfeature = features.Feature(geom,attributes)
            print(newfeature)
            # # Add feature to existing hosted feature layer
            # result = HFS_item.layers[0].edit_features(adds = [newfeature])