import json
import googlemaps

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


def set_insurance(req):
    fb_id = req["originalDetectIntentRequest"]["payload"]["data"]["sender"]["id"]

    insurance = req["queryResult"]["queryText"]

    users[fb_id]["insurance"] = {
      "insurance": insurance
    }

    plans = ["aetna awesome 1", "aetna week 2", "aetna poor 3"]
    # todo get plans 

    quick_replies = list(map(lambda plan: {
        "content_type":"text",
        "title":plan,
        "payload":plan
    }, plans))

    obj = {
        "fulfillmentText": "111 ...111?",
        "payload": {
            "fulfillmentText": "test mesasage?",
            "facebook": {
                "text": "Alright. What plan do you have?",
                "quick_replies": quick_replies
            }
        },
        "source": "server"
    }


    return obj



    # return {
    #     "fulfillmentText": "Alright. Here are some doctors by you."
    # }

    # return {
    #     "fulfillmentText": "fuckkers.",
    #     "facebook": {
    #         "text": "Sure thing, please share your current location",
    #         "quick_replies": [
    #             {
    #                 "content_type": "location"
    #             }
    #         ]
    #     }

    # }