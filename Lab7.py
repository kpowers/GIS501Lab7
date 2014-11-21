from TwitterSearch import *
from geopy import geocoders
import arcpy
from arcpy import env

def geo(location):
    g = geocoders.GoogleV3()
    loc = g.geocode(location)
    return loc.latitude, loc.longitude
#Create empy array variable.
array = arcpy.Array()
point = arcpy.Point()
#be able to overwrite data
arcpy.env.overwriteOutput = True
#WHERE YOU WANT YOUR NEW FILE
filelocation = "C:/Users/snackpowers/Documents/GIS501_Directory/GIS501_week8/"
#place to put turtle feature class
fc = "C:/Users/snackpowers/Documents/GIS501_Directory/GIS501_week8/twitter.shp"
#set spatial reference for shapefile you will create
spatialref = "C:/Users/snackpowers/Documents/GIS501_Directory/WGS 1984.prj"

#Create point feature class
arcpy.management.CreateFeatureclass(filelocation, "twitter", "POINT","","","",spatialref)
arcpy.management.AddField(fc, "lat", "FLOAT")
arcpy.management.AddField(fc, "lng", "FLOAT")
arcpy.management.AddField(fc, "Tweet", "TEXT")
#USE THE SHAPE@XY TOKEN TO ADD POINTS TO A POINT FC
cursIns = arcpy.da.InsertCursor(fc, ["SHAPE@XY", "Tweet"])

try:
    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.set_keywords(['Dybbuugb']) # let's define all words we would like to have a look for

    tso.set_include_entities(False) # and don't give us all those entity information

    #object creation with secret token. Twitter API crap.
    ts = TwitterSearch(
        consumer_key = 'hsveGVbEICZkVlHNZEGub19W0',
        consumer_secret = 'b3KpbMZzBNUfHt142f0x89pYdC3hPolAh49qGJ6Lv2VOh49bzH',
        access_token = '2864982447-SmV6q4ArJGOv620JlwX4byUpKnQ8hDHK4MgnqX3',
        access_token_secret = 't7RsfbC40H2yyctjjg7HXbcDduEa1nY9554z8OPXXde1q'
     )

     # this is where the fun actually starts :)
    for tweet in ts.search_tweets_iterable(tso):
        print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
        if tweet['place'] is not None:
            (lat, lng) = geo(tweet['place']['full_name'])
            print 'And they said it from (' + str(lat) +', ' +str(lng)+')'
            text = (str(tweet['text']), str(tweet['created_at']))
            print text
            cursIns.insertRow(tweet)
        else:
            print "And their place wasn't specified..."
            #(lat,long) = [("None", "None")]

except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)

#del cursIns
