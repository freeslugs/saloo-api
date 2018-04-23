import re
import json
import googlemaps
import bs4
import urllib.request
import requests
import numpy as np
import pandas as pd
import threading
import time
import random

gmaps = googlemaps.Client(key='AIzaSyBNAzQkOEm1dFe95yBBYI5aIufd1MwHQ9w')

users = {}

def get_fb_id(req):
    return req["originalDetectIntentRequest"]["payload"]["data"]["sender"]["id"]

def set_location(req):
    location = req["queryResult"]["outputContexts"][0]["parameters"]
    reverse_geocode = gmaps.reverse_geocode((location["lat"], location["long"]))
    address = reverse_geocode[0]["formatted_address"]

    fb_id = get_fb_id(req)

    if fb_id in users:
        print(json.dumps(users[fb_id], indent=4))

        if "insurance_plan" in users[fb_id]:
            insurance_plan = users[fb_id]["insurance_plan"]
            insurance_carrier = users[fb_id]["insurance_carrier"]
            address = users[fb_id]["address"]

            threading.Thread(target=async_get_doctors, args=(fb_id, address, insurance_carrier, insurance_plan)).start()

            return {
                "fulfillmentText": "Finding a doctor is taking longer than expected. Can you try again?",
                "followupEventInput": {
                    "name": "GET_DOCTORS"
                }
            }
        
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

def get_provider(insurance):
    loc = 'https://api.zocdoc.com/directory/v1/insurances/autocomplete?text=' + insurance + '&insurance_type=health&directory_id=-1'
    r = requests.get(loc)
    insurance_providers = r.json()
    insurance_providers = list(filter(lambda x: x["plan_id"] == None, insurance_providers))
    if(len(insurance_providers) == 0):
        return None
    sorted_list = sorted(insurance_providers, key=lambda x: x["rank"], reverse=True)
    return sorted_list[0]

def get_plans(provider):
    loc = 'https://api.zocdoc.com/directory/v1/insurances/autocomplete?text=' + provider["carrier_name"] + '&insurance_carrier=' + str(provider["carrier_id"]) + '&insurance_type=health&directory_id=-1'
    r = requests.get(loc)
    plans = r.json()
    plans = list(filter(lambda x: x["plan_id"] != None, plans))
    if(len(plans) == 0):
        return []
    sorted_list = sorted(plans, key=lambda x: x["rank"], reverse=True)
    return sorted_list[0:5]

def set_insurance(req):
    fb_id = get_fb_id(req)
    insurance = req["queryResult"]["queryText"]

    provider = get_provider(insurance)

    users[fb_id]["insurance_carrier"] = provider["carrier_id"]

    if(provider == None):
        return {
            "fulfillmentText": "Couldn't find that provider. Try 'Aetna'.",
            "followupEventInput": {
                "name": "REQUEST_INSURANCE"
            }
        }

    plans = get_plans(provider)
    text = "Alright. I see your insurance provider is " + provider['carrier_name'] + ". What plan do you have?"

    quick_replies = list(map(lambda plan: {
        "content_type":"text",
        "title":plan["plan_name"],
        "payload":plan["plan_id"]
    }, plans))

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

def async_get_doctors(fb_id, address, insurance_carrier, insurance_plan):
    global users
    print ("%s %s %s %s %s" % (threading.current_thread(), str(fb_id), address, str(insurance_carrier), str(insurance_plan)))

    loc = 'https://www.zocdoc.com/search?address=' + address.replace(" ", "%20") + '&insurance_carrier=' + str(insurance_carrier) + '&day_filter=AnyDay&gender=-1&language=-1&offset=0&insurance_plan=' + str(insurance_plan) + '&reason_visit=75&after_5pm=false&before_10am=false&sees_children=false&sort_type=Default&dr_specialty=153&ip=160.39.9.117'
    page = urllib.request.urlopen(loc)
    soup = bs4.BeautifulSoup(page,'html.parser')
    container = soup.find_all("div", class_="js-search-prof-list")[0]
    
    names = container.find_all("a", class_="ch-prof-link")
    ratings = container.find_all("div", class_="ch-prof-row-rating")        
    images = container.find_all("img", class_="ch-prof-img")

    addresses = container.find_all("div", class_='js-search-prof-row-address')
    for address in addresses:
        for a in address.find_all("div"):
            a.decompose()
    
    doctors = []

    for i in range(len(names)):
        name = names[i].getText().strip().replace("\n","").replace("  ","")
        # get rating
        regex = r"\d_\d"
        res = re.findall(regex,str(ratings[i]))[0]
        rating = float(res.replace("_","."))
        # get address
        address_list = addresses[i].getText().split('\n')
        address = ' '.join(list(map(lambda x: x.strip(), address_list))).strip()
        # get image
        image = "https:" + images[i]['src']

        doctors.append({
            'name': name,
            'rating': rating, 
            'address': address,
            'image': image
        })

    users[fb_id]["doctors"] = doctors

def get_doctors(req):
    fb_id = get_fb_id(req)

    if "doctors" not in users[fb_id]:
        print ("Start : %s" % time.ctime())
        time.sleep( 2 )
        print ("End : %s" % time.ctime())
        if "doctors" not in users[fb_id]:
            return {
                "fulfillmentText": "Finding a doctor is taking longer than expected. Can you try again?",
                "followupEventInput": {
                    "name": "GET_DOCTORS"
                }
            }

    doctors = users[fb_id]["doctors"]

    text = "Here are some nearby doctors covered by your insurance."

    elements = list(map(lambda doctor: {
        "title": doctor["name"],
        "image_url": doctor["image"],
        "subtitle": "Rating: " + str(doctor["rating"]) + "\n Address: " + doctor["address"],
        "buttons": [{
            "title": "Directions",
            "type": "web_url",
            "url": "https://maps.google.com/?q=" + doctor["address"]
        }]
    }, doctors))

    obj = {
        "fulfillmentText": text,
        "payload": {
            "fulfillmentText": text,
            "facebook": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "top_element_style": "LARGE",
                        "elements": elements[0:4]
                    }
                }
            } 
        },
        "source": "server"
    }

    return obj

def set_plan(req):
    fb_id = get_fb_id(req)
    plan = req["queryResult"]["queryText"]

    users[fb_id]["insurance_plan"] = plan

    insurance_plan = users[fb_id]["insurance_plan"]
    insurance_carrier = users[fb_id]["insurance_carrier"]
    address = users[fb_id]["address"]

    threading.Thread(target=async_get_doctors, args=(fb_id, address, insurance_carrier, insurance_plan)).start()

    return {
        "fulfillmentText": "Finding a doctor is taking longer than expected. Can you try again?",
        "followupEventInput": {
            "name": "GET_DOCTORS"
        }
    }