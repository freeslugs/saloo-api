import json
import googlemaps
import bs4
import urllib.request
import requests
import numpy as np
import pandas as pd

gmaps = googlemaps.Client(key='AIzaSyBNAzQkOEm1dFe95yBBYI5aIufd1MwHQ9w')

users = {}

def set_location(req):
    
    location = req["queryResult"]["outputContexts"][0]["parameters"]
    reverse_geocode = gmaps.reverse_geocode((location["lat"], location["long"]))
    address = reverse_geocode[0]["formatted_address"]

    fb_id = req["originalDetectIntentRequest"]["payload"]["data"]["sender"]["id"]

    users[fb_id] = {
        "location": location,
        "address": address
    }

    return {
        "fulfillmentText": "Alright, what's your insurance provider?",
        "followupEventInput": {
            "name": "REQUEST_INSURANCE"
        }
    }


def get_providers(insurance):
    loc = 'https://api.zocdoc.com/directory/v1/insurances/autocomplete?text=aetna&insurance_type=health&directory_id=-1'
    r = requests.get(loc)
    insurance_providers = r.json()
    filtered_insurance_providers = list(filter(lambda x: x['carrier_name'] == insurance and x["plan_id"] != None, insurance_providers))
    # todo: sort by "rank"
    df = pd.DataFrame(filtered_insurance_providers)
    top_three = df.sort_values('plan_name')["plan_name"][0:3]
    return top_three

def set_insurance(req):
    fb_id = req["originalDetectIntentRequest"]["payload"]["data"]["sender"]["id"]

    insurance = req["queryResult"]["queryText"]

    users[fb_id]["insurance"] = {
      "insurance": insurance
    }

    plans = get_providers(insurance)

    quick_replies = list(map(lambda plan: {
        "content_type":"text",
        "title":plan,
        "payload":plan
    }, plans))

    text = "Alright. What plan do you have?"

    obj = {
        "fulfillmentText": text,
        "payload": {
            "fulfillmentText": text,
            "facebook": {
                "text": text,
                "quick_replies": quick_replies
            }
        },
        "source": "server"
    }

    return obj