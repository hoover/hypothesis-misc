#!/usr/bin/python3.4
import requests
import json
import configparser
import redis
import time
import argparse

# Find out which config file we want to read
parser = argparse.ArgumentParser()
parser.add_argument('--config', help='Read the configuration from this file',
                    default='/etc/h_to_rocket_chat.conf')
args = parser.parse_args()
config_file = args.config

# Read the config file
try:
    config = configparser.ConfigParser()
    config.read(config_file)
    redis_host = config['redis']['host']
    redis_port = config['redis']['port']
    redis_db = config['redis']['database']
    hypothesis_url = config['hypothesis']['url']
    hypothesis_search_params = config['hypothesis']['search_params']
    hypothesis_api_token = config['hypothesis']['api_token']
    rocketchat_endpoint = config['rocketchat']['endpoint']
    rocketchat_path = config['rocketchat']['path']
    rocketchat_auth_token = config['rocketchat']['auth_token']
except Exception as e:
    print('Can not read config file: %s' % e)
    exit(3)

# Connnect to the Redis database, which will be used to store the IDs and links
# of the annotations we have already sent to the Rocket chat channel
try:
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
except Exception as e:
    print('Can not connect to Redis: %s' % e)
    exit(3)

# This function will take the various pieces of information from an annotation
# and construct a message and post it to a Rocket chat channel
def post_to_rocket_chat(rc_endpoint,rc_path,rc_token,message,title,link,
                        text,source):
    rc_headers = {'Authorization': 'Bearer ' + rc_token,
                 'Content-Type': 'application/x-www-form-urlencoded'}
    rc_payload = 'payload={"text":"%s", "attachments":[{"title":"%s",\
                  "title_link":"%s", "text":"Source: %s. %s",\
                  "color":"#764FA5"}]}' % (message, title, link, source, text)
    rc_request = requests.post(rc_endpoint + rc_path, headers=rc_headers,
                  data=rc_payload.encode('utf-8'))

# Check if the annotation ID is in Redis a.k.a. has already been sent to chat
def check_id_in_redis(annotation_id):
    if r.get(annotation_id) == None: return False
    else: return True

# Call the Hypothesis API endpoint and get annotations based on the search
# term found in the config file
def get_annotations():
    h_cookies = dict(h_api_auth=hypothesis_api_token)
    h_search = hypothesis_search_params
    h_request = requests.get(hypothesis_url + h_search, cookies=h_cookies)
    h_result = json.loads(h_request.text)
    return h_result

# Get the annotations, extract the info we need from them, store in Redis and
# post them to Rocket chat
def main():
    try:
        annotations = get_annotations()
    except Exception as e:
        print('Can not get the annotations from Hypothesis: %s' % e)
        exit(3)
    for row in annotations['rows']:
        h_id = row['id']
        if 'title' in row['document']: h_title = row['document']['title'][0]
        else: h_title = '<No title>'
        h_text = row['text']
        h_source = row['uri']
        h_link = row['links']['html']
        h_user = row['user'].split(':')[1].split('@')[0]
        h_tags = " ".join([str(x) for x in row['tags']] )
        if check_id_in_redis(h_id) == False:
            try:
                r.set(h_id, h_link)
            except Exception as e:
                print('Can not write the annotation ID to Redis: %s' % e)
                exit(3)
            message = "@%s created a new annotation. Tags: %s" % (h_user,h_tags)
            try:
                post_to_rocket_chat(rocketchat_endpoint,rocketchat_path,
                                    rocketchat_auth_token,message,h_title,
                                    h_link,h_text,h_source)
            except Exception as e:
                print('Can not post to Rocket chat: %s' % e)
                exit(3)

# We want to run this script under supervisor, so go run through the main loop
# endlessly, with a short break and let supervisor take care of the rest
if __name__ == '__main__':
    time.sleep(7)
    while True:
        main()
        time.sleep(3)
