# Hypothesis to Rocket Chat

This is a small script meant to be run under [Supervisor](http://supervisord.org/). There is an example Supervisor config for it. Its purpose is to parse [Hypothesis](https://hypothes.is/) annotation stream via its API and post any new annotations to a [Rocket Chat](https://rocket.chat/) grain that is hosted in [Sandstorm](https://sandstorm.io/).

## How does it work
First of all you need a working Rocket Chat grain and you also need a local Hypothesis install. Of course, this can work with the publicly hosted Hypothes.is, but it was written for a custom, local install. The script will parse the annotation stream every 3 seconds, determine via a Redis cache which annotation hasn't been posted to Rocket Chat yet and post it to the channel you have configured in its config file.

## Requirements

* a (Linux preferably) host running Python 3.x
* make sure your local Hypothesis' API and the Rocket Chat + Sandstorm API is available from the host you are going to run this script from
* the [Python Requests](http://docs.python-requests.org/en/master)  module installed on said host
* [Redis server](http://redis.io/) installed on the same host and the [Python Redis client](https://pypi.python.org/pypi/redis)

## Before you start
* You will need to get the API endpoint for the Rocket chat grain from Sandstorm. To do this, you need to click on the key icon in top bar in the Rocket chat grain. Give the key a label (Api for example) and click on 'Create'. Write down the link up until the # sign. For example, if you key looks like https://api-edbe62c2c5e71227153aae4c.my.sandstorm.domain#VCE9H-P-k10lkV9XosDowW1-ZCSR3DvEqISj7jaJO9a
you will just need https://api-edbe62c2c5e71227153aae4c.my.sandstorm.domain.
* Next, you will need to configure a new 'Integration' in Rocket chat. For this you need to have administrative rights to this Rocket chat instance. Go to its admin panel and click on 'Integrations'. Create a new integration, click on 'Incoming webhook'. Configure the options there to your liking. Write down from that page the 'Webhook URL' and the 'Token'. Save this integration to activate it.

## Installation

* either git clone [this repo](https://github.com/hoover/hypothesis-misc.git) on this host or download its [tarball](https://github.com/hoover/hypothesis-misc/archive/master.zip)
* rename the provided example config file - mv h_to_rocket_chat.conf.example h_to_rocket_chat.conf - and open it in your preferred editor
* edit the config file, the options are pretty self-explanatory. The only part you need to be careful with is the [rocketchat] config section:
    - the 'endpoint' should be the above generated endpoint followed by '/hooks'. Following the example above, this entry should look like 'https://api-edbe62c2c5e71227153aae4c.my.sandstorm.domain/hooks'
    - the 'path' entry should be just the part after the last slash in the 'Webhook URL'. So if the 'Webhook URL' you got from Rocket chat looked like this: 'http://127.0.0.1:8000/hooks/Z3MDTS8hQ4u3qLoYt/m3k8cySXDDsMPHBtJ59yxeBT6knopD9BniGGiRFrtuC6bvdQ', your 'path' entry in the config file should be just this: 'Z3MDTS8hQ4u3qLoYt/m3k8cySXDDsMPHBtJ59yxeBT6knopD9BniGGiRFrtuC6bvdQ'
    - the 'auth_token' entry is just the 'Token' entry you have written down from Rocket chat's Incoming webhook page
* You can now run the script by pointing it to this config file you have just created. Let's say you have git cloned / downloaded the script in /opt. You can run it like this:
```
/opt/hypothesis-misc/h_to_rocket_chat/h_to_rocket_chat.py --config /opt/hypothesis-misc/h_to_rocket_chat/h_to_rocket_chat.conf
```
* If everything is fine, the script should be running and not outputting anything. Try to create a new annotation and you should see it in the Rocket chat channel you have defined in the Incoming webhook.

## Supervisor config
The repo has a provided supervisor config example. Just copy it in the /etc/supervisor.d/ directory and edit it accordingly. Reload supervisord.
