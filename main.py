import urllib2
import json
import datetime
import re
import os # Needed for AWS Lambda function environment variable

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.fcc3ac73-145e-42cb-b756-1697a003b4d5"):
        raise ValueError("Invalid Application ID")   
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetReleases":
        return get_releases()
    elif intent_name == "GetPlatformReleases":
        return get_platform_releases(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Thanks from Gameskill!"
    speech_output = "Thank you for using Gameskill...  Noob!"
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Hello from Gameskill!"
    speech_output = "Welcome to Gameskill! " \
                    "You can ask me for release dates on games and platforms."
    reprompt_text = "Please ask me for a release date."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }
    
def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
    
### BEGIN INTENTS #######
api_key     = os.environ['api_key']
myformat    = '&format=json'
sort        = '&sort=original_release_date:asc'
base_url    = 'http://www.giantbomb.com/api/games/?api_key=' + api_key + myformat + sort

def get_releases():
    session_attributes  = {}    
    card_title          = "Current Month Releases"
    speech_output       = "I need more information. Say something like, What playstation 4 games are coming out next month?"
    reprompt_text       = "Say something like, What playstation 4 games are coming out next month?"
    should_end_session  = False
    return build_response(session_attributes, build_speechlet_response(
       card_title, speech_output, reprompt_text, should_end_session))
       
def get_platform_releases(intent):
    session_attributes  = {}    
    card_title          = "Current Month Releases"
    speech_output       = "I can't find any games. Say something like, What playstation 4 games are coming out next month?"
    reprompt_text       = "Say something like, What playstation 4 games are coming out next month?"
    should_end_session  = False
    platform = intent["slots"]["Platform"]["value"]
    alexa_date = intent["slots"]["Date"]["value"]
    datefilter = convert_date(alexa_date)
    my_game_list = construct_game_list(datefilter)
    secondfilter = filter_platform(my_game_list, platform)
    if len(secondfilter) > 0 :
        speech_output = speak_list(secondfilter)
    return build_response(session_attributes, build_speechlet_response(
       card_title, speech_output, reprompt_text, should_end_session))


### END INTENTS #######
### BEGIN INTENT HELPERS #######

# http://www.giantbomb.com/api/games/?format=json&api_key=8f265801cbb0a6dbf987730c6b252cd7484c0636&offset
def construct_game_list(filter) :
    """
    Returns a list (of lists and dicts) of games after constructing a URL and querying giantbomb API.
    Because the response can have max up to 100 results limit, the list is iterated through using 
    offset to compile every page.

    API supports only one filter, so platform is filtered in a another helper function.
    Expects to receive param in following format:
    '&filter=original_release_date:2017-01-01|2017-01-31'
    or
    '&filter=original_release_date:2017-01-01'
    """
    offset_count = 0
    offset  = '&offset=' + str(offset_count)
    url = base_url + filter + offset
    response = urllib2.urlopen(url)
    releases = json.load(response)
    results = releases['results'] 
    limit = releases['limit']
    while releases['number_of_total_results'] > releases['offset'] + releases['number_of_page_results'] :
        offset = '&offset=' + str(offset_count + limit)
        url = base_url + myformat + filter + sort + offset
        response = urllib2.urlopen(url)
        releases = json.load(response)
        results = results + releases['results']
    print url
    return results  

# filter_platform(my_game_list, platform)
def filter_platform(game_list, platform):
    """
    The API URL can only filter on one thing at a time. So to apply a second filter, we
    need to iterate through the list that is returned from the json data.
    """
    output_list = []
    nodate = None
    onplatform = None
    unicodeerror = None
    for i in game_list : # filters out platforms
        try :
            print i['name'] 
        except UnicodeEncodeError :
            unicodeerror = True
        if i['platforms'] != None :            
            for p in i['platforms'] :
                if p['abbreviation'] == platform or p['name'] == platform :
                    onplatform = True
        if i['original_release_date'] != None :
            releasedate = i['original_release_date']
            releasedate = releasedate[:-9]          
        elif i['expected_release_day'] != None:
            releasedate = str(i['expected_release_year']) + '-' + str(i['expected_release_month']) + '-' + str(i['expected_release_day']) 
        else :
            nodate = True
        if nodate != True and onplatform == True and unicodeerror != True: 
            mydict = { \
                'id' : i['id'], \
                'name' : i['name'], \
                'release_date' : releasedate, \
                'platform' : platform}
            output_list.append(mydict)
    return output_list



#print json.dumps(results_dict, sort_keys=True, indent=4, separators=(',', ': '))

def convert_date(isodate) :
    """
    Takes a date in the format that Alexa provides from AMAZON.date
    Figures out what the range should be and formats it for use in url string. 
    Should look like:
    2016-12-1|2016-12-31
    """
    # Check for single date
    if re.search(r'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', isodate) != None :
        startdate = datetime.datetime.strptime(isodate, '%Y-%m-%d').date()
        enddate = startdate
    # Check for month
    elif re.search(r'[0-9][0-9][0-9][0-9]-[0-9][0-9]', isodate) != None :
        startdate = datetime.datetime.strptime(isodate, '%Y-%m').date()
        enddate = add_one_month(startdate) - datetime.timedelta(days=1)
    # Check for week
    elif re.search(r'[0-9][0-9][0-9][0-9]-[W][0-9][0-9]', isodate) != None :
        startdate = datetime.datetime.strptime(isodate + '-0', "%Y-W%W-%w").date()
        enddate = startdate + datetime.timedelta(days=7)
    startdate = startdate.isoformat()
    enddate = enddate.isoformat()
    url_date = startdate + '|' + enddate
    myfilter  = '&filter=original_release_date:' + url_date
    print myfilter
    return myfilter

def add_one_month(t):
    """Return a `datetime.date` or `datetime.datetime` (as given) that is
    one month earlier.
    
    Note that the resultant day of the month might change if the following
    month has fewer days:
    
        >>> add_one_month(datetime.date(2010, 1, 31))
        datetime.date(2010, 2, 28)
    
    Code was found here, give props:
    http://code.activestate.com/recipes/577274-subtract-or-add-a-month-to-a-datetimedate-or-datet/    
    """
    one_day = datetime.timedelta(days=1)
    one_month_later = t + one_day
    while one_month_later.month == t.month:  # advance to start of next month
        one_month_later += one_day
    target_month = one_month_later.month
    while one_month_later.day < t.day:  # advance to appropriate day
        one_month_later += one_day
        if one_month_later.month != target_month:  # gone too far
            one_month_later -= one_day
            break
    return one_month_later

def speak_list(mylist) :
    output = ''
    for i in mylist :
        name = str(i['name'])
        platform = str(i['platform'])
        release_date = i['release_date']
        output = output + name + ' on ' + platform + ' release date is ' + release_date + '. '
    # output = '. '.join(i['name'] + ' on ' + i['platform'] + ' release date is ' + i['release_date']  for i in mylist)
    return output

