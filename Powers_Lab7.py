#December 2014, GIS502 Lab7/Final Project
#Searches twitter data through the REST API using the TwitterSearch Library
#outputs files to a shapefile.
#Current search terms inlcude Gateway Pacific Terminal, beyondcoalWA...
#I believe the search time limit is 2 weeks. The Twitter API has a search limit of 1%? and times out every 15 min
#The google geocoder times out after__ and has a 24 hour wait time.
#Look up the documentation for geopy... get a token for increased rate. make an if/then statement

from TwitterSearch import *
from geopy import geocoders
import arcpy
from arcpy import env
import csv
import time #need to pause code at call limitation


#load geocoder
def geo(location): #
    g = geocoders.GoogleV3()
    loc = g.geocode(location)
    return loc.latitude, loc.longitude
#x,y = geocode(city) assigns the lat and long to x, y

#Create empy array variable.
point = arcpy.Point()
#be able to overwrite data
arcpy.env.overwriteOutput = True

#WHERE YOU WANT YOUR NEW FILE
filelocation = "C:/Users/snackpowers/Documents/GIS501_Directory/GIS501_week8/"
#place to put new feature class
fc = "C:/Users/snackpowers/Documents/GIS501_Directory/GIS501_week8/gateway_4.shp"
#set spatial reference for shapefile you will create
spatialref = arcpy.SpatialReference ('WGS 1984')

#Create point feature class
arcpy.management.CreateFeatureclass(filelocation, "gateway_4.shp", "POINT","","","",spatialref)
arcpy.management.AddField(fc, "LAT", "FLOAT","","",20,"","NULLABLE")
arcpy.management.AddField(fc, "LNG", "FLOAT", "","",20,"","NULLABLE")
arcpy.management.AddField(fc, "USER_NAME", "TEXT","","",40,"","NULLABLE")
arcpy.management.AddField(fc, "TWEET", "TEXT","","",140,"","NULLABLE")
arcpy.management.AddField(fc, "TWEET_DATE", "TEXT","","",40,"","NULLABLE")
arcpy.management.AddField(fc, "SEARCHTERM", "TEXT","","",40,"","NULLABLE")

#USE THE SHAPE@XY TOKEN TO ADD POINTS TO A POINT FC
cursIns = arcpy.da.InsertCursor(fc, ("SHAPE@XY", "LAT", "LNG", "USER_NAME", "TWEET","TWEET_DATE"))
cursup = arcpy.da.UpdateCursor(fc, ["SHAPE@XY"])


try:
    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    # let's define all words we would like to have a look for. Create a list to search through.
    tso.set_keywords([search_term])
    tso.add_keyword(['Seahawks'])
    #Dybbuugb
    #tso.set_geocode(47.417566, -120.277099, 180,000, False) #Sets location and range true for meters false for miles
    tso.set_include_entities(False) # and don't give us all those entity information
    

    #object creation with secret token. Twitter API crap.
    ts = TwitterSearch(
        consumer_key = '0lEQUqfgr5gt8RniBu0duCHgD',
        consumer_secret = 'HPfxpYBbSr9iPUnyNc7oCjQl8n5AJH3CCrXkx4jFhVj8tN4mbL',
        access_token = '2864982447-reIhQZ4A1Zjz8vv6tUKqaSjVPcfsWeVBHMxaBZm',
        access_token_secret = 'R99CWnEtA5nCrseI3iTCrOdjkXUce2m1J2oAyxfQwo6nW'
     )


    # iterate through search terms in the twitter API. Only english entries output.
    for tweet in ts.search_tweets_iterable(tso):
        #only pull English tweets
        if (tweet['lang'] == 'en'):
            #commented out // lot's of tweets don't have GPS enabled so they wont have coordintes. if you print tweets here you'll see 100% of tweets instead of just tweets with coordinates
            #print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
            if tweet['coordinates'] is not None: #check to see if tweet geotagged. If not, [0.0, 0.0] or None will be there.
                print ( '@%s tweeted: %s, on %s' % ( tweet['user']['screen_name'], tweet['text'], tweet['created_at'] ) )
                C = (tweet['coordinates']) #grab the dictionary containing coordinates
                C = C.get('coordinates') #get only the coordinates
                lat = C[1]  #lat is the second one
                lng = C[0]  #Lng is the first
                print "from geot-tagged location: {}, {}".format(lat, lng)

            elif tweet['place'] is not None: # search for a location entered as text, not coordinates
                (lat, lng)= geo(tweet['place']['full_name'])
                print '(place) And they said it from (' + str(lat) +', ' +str(lng)+')'

            elif tweet['user']['location'] is not None: # search for profile location
                try:
                    (lat, lng) = geo(tweet['user']['location'])
                    print ( '@%s tweeted: %s, on %s' % ( tweet['user']['screen_name'], tweet['text'], tweet['created_at'] ) )
                except Exception as e:
                    continue
            try:
                #setup text to put into shapefile or CSV
                text = (str(tweet['text'])) #this gave me a ascii error, the four lines below show how you can use the encode function on a string to make it utf-8 which is better for web data
            except UnicodeEncodeError as e:
                #continue #this is like a skip command. comment it out to make the code beneath it run.
                print "Error : ", e
                print "Error Text : ", tweet['text']
                #print "Converted to Unicode : ", tweet['text'].encode("utf-8")
                #print "take two : ", str(tweet['text'].encode("utf-8")), str(tweet['created_at'].encode("utf-8")) #shoud work every time
                text = str(tweet['text'].encode("utf-8"))
            username = tweet['user']['screen_name']
            created_at = str(tweet['created_at'])

            if lat == 0.0:
                continue
            else:
                point = arcpy.Point(lng, lat)
                cursIns.insertRow((point, lat, lng, username, text, created_at))
        else:
            continue

except (TwitterSearchException) as eg: 
    print "TwitterSearch limit exceded. Please wait 15 minutes"
    #pause for 15 minutes
    time.sleep(900)
    #update this with timeout error
except Exception as ef:
    #other errors
    print "Error: ", ef
    #continue

del cursIns
