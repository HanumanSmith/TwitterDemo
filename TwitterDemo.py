import ssl
from functools import wraps
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar

ssl.wrap_socket = sslwrap(ssl.wrap_socket)

from twitter import *
import time
import datetime
from SendGmail import send_mail
import sys

def get_trend():
    '''Use the Twitter API to pull a list of the Top Trends.
    Results can be localized using a WOE ID. Returns a
    string naming the current #1 trend'''
    # load API credentials 
    config = {}
    execfile("GetTrendConfig.py", config)
    # create twitter API object
  
    t = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))
    
    # retrieve global trends.
    # other localised trends can be specified by looking up WOE IDs:
    #   http://developer.yahoo.com/geo/geoplanet/
    # twitter API docs: https://dev.twitter.com/docs/api/1/get/trends/%3Awoeid
    results = t.trends.place(_id = 23424977)
    
    for location in results:
            for trend in location["trends"]:                
                print '#1 Trend: ', str(trend["name"])

                return str(trend["name"])
                

def get_time(ts):
    '''Function is passed a timestamp and converts to readable datetime'''
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    return st

def convert_trend(trend):
    '''Function is passed a trend from which any # present are stripped.
    It then does the same for Spaces. Finally, it places a # at the front
    and returns the resulting Hashtag as a String'''
    stripped_trend = trend.replace("#", "")
    double_stripped_trend = stripped_trend.replace(" ", "")
    converted_trend = "#" + double_stripped_trend
##    print converted_trend
    return converted_trend

def check_log(log, tweet):
    '''Function is passed a Text log of previous tweets, and the newly
    proposed tweet. Checks for the new tweet against the log. Returns
    True or False'''
    if tweet in open('Tweet Log.txt').read():
##        print 'Check Log MATCH', tweet, log
        return True
    else:
##        print 'Check Log NO MATCH', tweet, log
        return False

config = {}
execfile("SendTweetConfig.py", config)

t = Twitter(auth=OAuth(config['access_token'], config['access_token_secret'], config['consumer_key'], config['consumer_secret']))

restart_count = 0
mail_attempt = 0
while restart_count < 5:
    try:
        first_trend = get_trend()
        ts = time.time()
        check_trend = ' ' + convert_trend(first_trend.lower())
        if check_log('Tweet Log.txt', check_trend):
            print 'MATCH - Rejected Tweet: ', convert_trend(first_trend), get_time(ts)                       
        else:
            print 'NO MATCH - Approved Tweet: ', convert_trend(first_trend), get_time(ts)
            t.statuses.update(status=convert_trend(first_trend) + " is the best")
            with open('Tweet Log.txt', 'a') as myfile:
                myfile.write(check_trend)
            myfile.close()
        restart_count = 0
        time.sleep(120)
    except KeyboardInterrupt:
        print 'Program ended by user.'
        break
    except Exception, e:
        print str(e)
        try:
            send_mail(str(e))
            time.sleep(120)
            restart_count += 1
            print 'Restart count:', restart_count
            print 'Restarted'
            send_mail('Restarted')
            
        except Exception, er:
            print str(er)
            time.sleep(120)
            mail_attempt += 1
            print 'Try email again:', mail_attempt

        



