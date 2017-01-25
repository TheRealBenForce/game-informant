
import urllib2
import json
import datetime
import os # Needed for AWS Lambda function environment variable

baseurl = 'http://www.giantbomb.com/api/'
api_key = os.environ['api_key']
time = datetime.datetime.now()

field = ['', / ## 00
         '', / ## 00
         '', / ## 00
         '', / ## 00
         '', / ## 00
         '', / ## 00


]  
filt = 

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
        return current_month_releases()
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
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

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
    
    #########
field = ['expected_release_quarter',   ## 00
'expected_release_year', /     ## 00
        'expected_release_month', /    ## 00
        'expected_release_day', /      ## 00
        'name', /                      ## 00
        'platforms', /                 ## 00
    ]

field = ['', / ## 00
         '', / ## 00
         '', / ## 00
         '', / ## 00
         '', / ## 00
         '', / ## 00
         

] 

def current_month_releases(platform=''):
    session_attributes = {}
    card_title = "Current Month Releases"
    reprompt_text = ""
    should_end_session = False

    month = time.month
    url = baseurl + 'games/?api_key=' + api_key + '&format=json' + '&filter=expected_release_month:' + str(month) + '&field_list=expected_release_quarter,expected_release_month,expected_release_day,expected_release_year,name,platforms'
    response = urllib2.urlopen(url)
    releases = json.load(response)
    totalgames = len(releases['results'])
    i = 0
    while i < totalgames:
        # Filters out null months
        # Learn more about giant bonb and find out why there are so many.
        if releases['results'][i]['expected_release_month'] == month :
            print releases['results'][i]['name'].encode('utf-8')
        i = i + 1
    speech_output = "This is your current month release function"
    print url
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))    

#def fetch_json(url):
#    response = urllib2.urlopen(url)
#    html = response.read()
#    html_decoded = html.decode('utf8')
#    print response.read()
#    json_data = json.loads(html_decoded)
#    #return json_data
#    print json_data
#    return

#def search_gb(query, resource):
#    format = ('format', 'json')
#    q = ('query', query)
#    t = ('resources', resource)
#
#    list = []
#    list.append(api_key)
#    list.append(format)
#    list.append(q)
#    list.append(t)
#    url = baseurl + 'search/' "?" + urllib.parse.urlencode(list)
#    return url