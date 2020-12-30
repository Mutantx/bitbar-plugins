#!/usr/bin/python
# -*- coding: utf-8 -*-

# <bitbar.title>Dorba Trail Status</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Mutantx</bitbar.author>
# <bitbar.author.github>Mutantx</bitbar.author.github>
# <bitbar.desc>Trail status for DORBA managed trails</bitbar.desc>

try:
    # Python2
    import httplib as importedhttpclient
    import json
except ImportError:
    # Python3
    import http.client as importedhttpclient
    import json
from math import radians, cos, sin, asin, sqrt # For Proximity haversine


def call_dorba():
    conn = importedhttpclient.HTTPSConnection("www.dorba.org", timeout=15)
    conn.request("GET", "/services/trails.php?")
    res = conn.getresponse()
    res_dorba_dict = json.loads(res.read())
    conn.close()
    return res_dorba_dict


def call_free_geo_ip():
    conn = importedhttpclient.HTTPSConnection('freegeoip.app', timeout=15)
    conn.request("GET", "/json/")
    res_latlong_dict = json.loads(conn.getresponse().read())
    conn.close()
    return res_latlong_dict


# haversine Reference: https://stackoverflow.com/a/4913653
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956 # Radius of earth in kilometers. Use 6371 for kilometers
    return c * r


def get_my_lat_long():
    try:
        LONGTITUDE
        LATITUDE
        print("Manually provided Long/Lat used")
        return float(LONGTITUDE), float(LATITUDE)
    except NameError:
        print("3rd Party provided Lat/Long given your IP")
        res_latlong_dict = call_free_geo_ip()
        return float(res_latlong_dict.get("longitude")), float(res_latlong_dict.get("latitude"))


def sort_by_my_lat_long(dict, my_long, my_lat):

    for i, x in enumerate(dict.get("trails")):
        x.get("trail")["distance_from_me"] = haversine(my_long, my_lat, float(x.get("trail").get("geoLang")),
                                                       float(x.get("trail").get("geoLat")))
    dict["trails"] = sorted(dict["trails"], key=lambda k: k.get("trail").get("distance_from_me"))
    return dict


def print_trails(dict):

    for i, x in enumerate(res_dict.get("trails")):
        emoji = ""
        if res_dict['trails'][i]['trail']['openClose'].lower() == "open":
            color = "green"
            # emoji = "🟢"
        elif res_dict['trails'][i]['trail']['openClose'].lower() == "closed":
            color = "red"
            emoji = "🔴"
        else:
            color = "yellow"
            emoji = "?"

        print("{0} {1}|dropdown=true".format(emoji, x.get('trail').get('trailName')))
        print("--Updated:{}".format(x.get('trail').get('updateFormatted')))
        print("-----")
        print("--Open/Closed Status: {0}|color={1}".format(x.get('trail').get('openClose'), color))
        print("--Description of Condition: {}".format(x.get('trail').get('conditionDesc')))
        print("--Land Owner: {}".format(x.get('trail').get('landOwner')))
        print("--DORBA Trail Page|href=https://www.dorba.org/trail.php?t={}".format(x.get('trail').get('trailId')))
        print("--Facebook Trail Page|href=https://www.dorba.org/trail.php?t={}".format(x.get('trail').get('facebook')))
        print("--Twitter Trail Page|href=https://www.dorba.org/trail.php?t={}".format(x.get('trail').get('facebook')))
        print("-----")
        print("--trailId:{}".format(x.get('trail').get('trailId')))
        print("--Lat:{}, Long:{}".format(x.get('trail').get("geoLat"), x.get('trail').get("geoLang")))
        if ORDER == "PROXIMITY":
            print("--IP: Distance to trail:{} miles".format(x.get('trail').get("distance_from_me")))


if __name__ == '__main__':

    # UPDATE SORTING PREFERENCES BELOW:
    # *Sorting Preferences*

    # Options:
    # 1: "ALPHABETICAL"     (DEFAULT) Revert back here if you encounter any issues with Proximity
    # 2: "PROXIMITY"        Free 3rd Party Service used, if LAT/LONG not manually provided, from your IP addr

    ORDER = "ALPHABETICAL"

    # *Manually Provide Latitude and Longitude*
    # Providing LAT/LONG manually removes call to 3rd Party Service freegeoip.app.  In some networks this service
    # may not be reachable.  Provide LAT/LONG manually below.
    #
    # Instructions: Remove # in front of both LONGTITUDE & LATITUDE.  Provide as number (without quotes).
    #               Acquiring LONGTITUDE LATITUDE can be as easy as right clicking on https://maps.google.com.
    #               Right Click on map(https://maps.google.com) > "What's here" feature provides it as well
    #               DFW Airport sample LONGTITUDE, LATITUDE provided below

    # LONGTITUDE = -97.04028155837426
    # LATITUDE = 32.899809080939946

    # UPDATE SORTING PREFERENCES ABOVE^

    print("DORBA")
    print("---")

    res_dict = call_dorba()

    if ORDER == "PROXIMITY":
        print("Proximity ENABLED")
        my_ip_longitude, my_ip_latitude = get_my_lat_long()
        print("Lat:{0} Long:{1}".format(my_ip_longitude, my_ip_latitude))
        print("---")
        res_dict = sort_by_my_lat_long(res_dict, my_ip_longitude, my_ip_latitude)

    print_trails(res_dict)
