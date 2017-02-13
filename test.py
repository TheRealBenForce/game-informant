
import urllib2
import json
import datetime
import re
import os # Needed for AWS Lambda function environment variable

# http://www.giantbomb.com/api/games/?format=json&api_key=8f265801cbb0a6dbf987730c6b252cd7484c0636&offset
def construct_game_dict(alexa_date='2015-11') :
    #api_key = os.environ['api_key']
    api_key = '8f265801cbb0a6dbf987730c6b252cd7484c0636'
    base_url = 'http://www.giantbomb.com/api/games/?api_key=' + api_key
    offset_count = 0
    offset  = '&offset=' + str(offset_count)
    myformat  = '&format=json'
    myfilter  = '&filter=original_release_date:' + convert_date(alexa_date)
    sort    = '&sort=original_release_date:asc'
    url = base_url + myformat + myfilter + sort + offset
    response = urllib2.urlopen(url)
    releases = json.load(response)
    results_dict = releases['results'] 
    limit = releases['limit']
    while releases['number_of_total_results'] > releases['offset'] + releases['number_of_page_results'] :
        offset = '&offset=' + str(offset_count + limit)
        url = base_url + myformat + myfilter + sort + offset
        response = urllib2.urlopen(url)
        releases = json.load(response)
        results_dict = results_dict + releases['results']
    print url
    return results_dict  

#print json.dumps(results_dict, sort_keys=True, indent=4, separators=(',', ': '))

def convert_date(isodate) :
    """
    Takes a date in the format that Alexa provides from AMAZON.date
    Figures out what the range should be and formats it for use in url string. 
    Should look like:
    2016-12-1%2000:00:00|2016-12-31%2023:59:59
    """
    if re.search(r'[0-9][0-9][0-9][0-9]-[0-9]', isodate) != None :      # For checking by month
        startdate = datetime.datetime.strptime(isodate, '%Y-%m').date()
        enddate = add_one_month(startdate) - datetime.timedelta(days=1)
    elif re.search(r'[0-9][0-9][0-9][0-9]-W[0-9]', isodate) != None :   # For checking by week (not done yet)
        startdate = datetime.datetime.strptime(isodate, '%Y-%m').date()
        enddate = startdate + datetime.timedelta(days=7)
    elif re.search(r'[0-9][0-9][0-9][0-9]-[0-9]', isodate) != None :      # For checking by day (not done)
        startdate = datetime.datetime.strptime(isodate, '%Y-%m').date()
        enddate = startdate 
    startdate = startdate.isoformat()
    enddate = enddate.isoformat()
    url_date = startdate + '%2000:00:00|' + enddate + '%2023:59:59'
    return url_date

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

def get_releases(game_list, platform=None): 
    if platform == None :
        print "Please provide a platform filter."
    session_attributes = {}
    card_title = "Current Month Releases"
    reprompt_text = ""
    should_end_session = False
    if platform != None :
        output_list = []
    for i in game_list :
        id = i['id']
        name = i['name']
        release_date = i['original_release_date']
        on_platform = None
        if i['platforms'] != None : 
            platforms = i['platforms']
            for p in platforms:
                if p['abbreviation'] == platform or p['name'] == platform :
                    on_platform = True
                    mydict = { \
                       'id' : i['id'], \
                       'name' : i['name'], \
                       'release_date' : i['original_release_date'], \
                       'platform' : p['name']}
                    output_list.append(mydict)
                    print name + ' for ' + p['name'] + ' on ' + release_date
    print output_list
    return output_list

def speak_dict(mydict) :
    for i in mydict :
        print i['name'] + \
        ' on ' + \
        i['platform'] + \
        ' release date is ' + \
        i['release_date'] 


game_list = construct_game_dict('2016-01')
get_releases(game_list, 'PC')
speak_dict(get_releases)