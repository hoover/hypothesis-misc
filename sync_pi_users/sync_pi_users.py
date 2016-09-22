#!/usr/bin/python3.4
import requests
import json
import subprocess
import string
import random
import configparser
import redis

# Read the config file
config = configparser.ConfigParser()
config.read('/etc/sync_pi_users.conf')
url = config['privacyidea']['url']
realm = config['privacyidea']['realm']
user = config['privacyidea']['user']
password = config['privacyidea']['password']
redis_host = config['redis']['host']
redis_port = config['redis']['port']

# Connect to Redis to read and store a cache of already added users to H
r = redis.StrictRedis(host=redis_host, port=redis_port)
users_in_redis = json.loads(r.get('h_users').decode('utf-8'))

# Function to generate random passwords for users
def generate_password(charsize):
    chars = string.ascii_letters + string.digits
    pwdSize = charsize
    return ''.join((random.choice(chars)) for x in range(pwdSize))

# Get an authentication token from Privacy Idea. This is usually valid for 1h
auth_payload = {'username': user, 'password': password}
auth_r = requests.post(url + '/auth', data=auth_payload)
auth_result = json.loads(auth_r.text)
token = auth_result['result']['value']['token']

# Use the previous auth token in a API request to PI to get a list of users
headers = {'Accept': 'application/json', 'Authorization': token}
user_r = requests.get(url + '/user?realm=' + realm, headers=headers)
users_response = json.loads(user_r.text)
users = users_response['result']['value']

# Go through the list of users and add them to Hypothesis unless they have
# been already added to it. We check that by comparing to the Redis cache
h_users = {}
for user in users:
    username = user['username']
    if user['email'] == '': email = 'admin@eic.network'
    else: email = user['email']
    passw = generate_password(15)

    if username in users_in_redis:
        pass
    else:
        h_users[username] = email
        subprocess.call(["/var/local/hypothesis/bin/run-h-add-user",
                        username, email, passw])

# Write the new list of synced users in Redis
 r.set('h_users', json.dumps(h_users))
