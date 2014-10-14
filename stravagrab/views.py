import json
import urllib2
import dateutil.parser
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from stravalib import Client

# You have a few syntax inconsistencies in this file where you're using camelCase instead of lowercase and underscores

def index(request):
    authorize_url= authenticate(request)
    return render(request, 'index.html', locals())


def convertDate(dateTimeStamp):
    d = dateutil.parser.parse(dateTimeStamp)
    return d.strftime('%m/%d/%Y')


def authenticate(request):
    client = Client()
    # This is prone to breaking everytime the URL changes, you may want to just get the current request's domain or use Django's sites
    # http://stackoverflow.com/questions/1451138/how-can-i-get-the-domain-name-of-my-site-within-a-django-template
    authorize_url = client.authorization_url(client_id=3255, redirect_uri='http://boiling-beyond-7936.herokuapp.com/stravaAuth')
    print authorize_url
    # Have the user click the authorization URL, a 'code' param will be added to the redirect_uri
    #return render_to_response('index.html', locals())
    return authorize_url

def stravaAuth(request):
    client = Client()
    # Extract the code from your webapp response
    code = request.REQUEST["code"]
    access_token = client.exchange_code_for_token(client_id=3255, client_secret='693de5acf6300d7e36d026a9bddeaa4ad89f765b', code=code)
    print access_token
    # Now store that access token somewhere (a database?)
    client.access_token = access_token
    athlete = client.get_athlete()

    # Store the athlete ID in the session for later use
    request.session["currentAthleteID"] = str(athlete.id)
    request.session["access_token"] = access_token
    request.session["is_authenticated"] = True
    is_authenticated = request.session["is_authenticated"]
    print("For {id}, I now have an access token {token}".format(id=athlete.id, token=access_token))
    userDetails =  getProfilePic(request)
    user_pic = userDetails["profile"]
    first_name = userDetails["firstname"]
    # now we're authenticated, go to this page to allow user to click link to get their starred segments
    # alternatively, why go here? why not just redirect to /selectStarredSegments
    #return render_to_response('stravaAuthenticated.html', locals())
    return render_to_response('index.html', locals())

def selectStarredSegments(request):
    #athleteID = "2775094" #niki
    #stravaBaseURL = "https://www.strava.com/api/v3/athlete/" + athleteID + "/segments/starred"
    # https://www.strava.com/api/v3/athlete/athlete_id=2775094/segments/starred"
    
    # Looks like you're often creating a strava url and passing in the access token, then making the request to get the data
    # You could abstract this out into it's own function so that you're not repeating this code
    stravaBaseURL = "https://www.strava.com/api/v3/segments/starred"
    accessTokenAthlete = "?access_token=" + request.session["access_token"]
    #accessTokenPublic = "?access_token=1419cd6da2e3adea1a813ac12d9aab14d8aa95c7"
    print stravaBaseURL + accessTokenAthlete
    # should use the "requests" library instead of urllib2, it's much nicer to use!
    # http://docs.python-requests.org/en/latest/
    response = urllib2.urlopen(stravaBaseURL + accessTokenAthlete)
    print response
    starredSegments = json.load(response)
    print starredSegments
    return render_to_response('index.html', locals())

def getEffortDetails(request, segmentInstanceId):
    #https://www.strava.com/api/v3/activities/197777105
    stravaBaseURL = "https://www.strava.com/api/v3/segment_efforts/"
    accessTokenAthlete = "?access_token=" + request.session["access_token"]
    #accessTokenAthlete = "&access_token=1419cd6da2e3adea1a813ac12d9aab14d8aa95c7"
    #print stravaBaseURL + segmentInstanceId + accessTokenAthlete
    response = urllib2.urlopen(stravaBaseURL + segmentInstanceId + accessTokenAthlete)
    effortDetails = json.load(response)
    #print response.average_speed
    return effortDetails


def getProfilePic(request):
    stravaBaseURL = "https://www.strava.com/api/v3/athlete/"
    accessTokenAthlete = "?access_token=" + request.session["access_token"]
    response = urllib2.urlopen(stravaBaseURL + accessTokenAthlete)
    profile = json.load(response)
    return profile

@csrf_exempt
def segmentEffort(request, id):
    stravaBaseURL = "https://www.strava.com/api/v3/segments/"
    segmentID = id
    effortsURL = "/all_efforts?athlete_id="
    athleteID = request.session["currentAthleteID"]
    #athleteID= "1819332"
    accessTokenAthlete = "&access_token=" + request.session["access_token"]
    # https://www.strava.com/api/v3/segments/:id/all_efforts
    #print stravaBaseURL + segmentID + effortsURL + accessTokenAthlete
    response = urllib2.urlopen(stravaBaseURL + segmentID + effortsURL + athleteID + accessTokenAthlete)
    segmentEffort = json.load(response)
    userDetails =  getProfilePic(request)
    first_name = userDetails["firstname"]

    segmentEffortDetail = []
    segmentEffortPace = []
    segmentEffortDates = []
    segmentEffortWatts = []

    for item in segmentEffort:
        effortID = getEffortDetails(request, str(item["id"]) ) #str(item["athlete"]["id"])
        segmentName = item["name"]

        try:
            #name = effortID["segment_efforts"][index]["name"]
            date =  effortID.get("start_date") #effortID["segment_efforts"][index]["start_date"]
            niceDate = convertDate(date)
            meters = effortID.get("distance") #effortID["segment_efforts"][index]["distance"]
            miles = meters * 0.00062137
            niceMiles = "{0:.2f}".format(miles)
            movingTime = effortID.get("moving_time")
            paceSeconds = movingTime/miles
            minutes = int(paceSeconds)/60
            seconds = int(paceSeconds)%60
            avgpace = str("{0:.0f}".format(minutes)) + "." + str("{:0>2d}".format(seconds))
            heartRate =  effortID.get("average_heartrate") #effortID["segment_efforts"][index]["average_heartrate"]
            watts = effortID.get("average_watts")
            komRank = effortID.get("kom_rank")
            prRank = effortID.get("pr_rank")

        except:
            print "exception on item "


        segmentEffortDetail.append({"date" : niceDate, "distance" : niceMiles, "pace" : avgpace, "heartRate" : heartRate, "watts" : watts, "komRank" : komRank, "prRank" : prRank})
        # segmentEffortMovingTime.append(movingTime)
        # segmentEffortDates.append(date)
        #for item in segmentEffortDetail:
        #	print item
    segmentEffortDetail.sort(key=lambda item:item["date"], reverse=True)

    for item in segmentEffortDetail:
        segmentEffortDates.append(item["date"])
        segmentEffortWatts.append(item["watts"])
        segmentEffortPace.append(item["pace"])

    return render_to_response('index.html', locals())
