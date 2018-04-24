# Saloo

A user-friendly chatbot that connects you to doctors near you that are covered by your health insurance.

## How it works

This is a facebook chatbot. We use DialogFlow (dialogflow.com, formally API.AI) to handle most of the conversational logic. 

Dialogflow is also connected to our Python Flask (flask.pocoo.org) server hosted on Heroku (heroku.com).

Our server connects to the Zocdoc (zocdoc.com) API to retreive doctor information. We then format the results and return them to the chatbot.

### Server 

Our server has two main files, app.py and handler.py. We copied the original layout from Dialogflow's docs. 

App.py sets up the Flask app, parses the requests and directs them to the right functions in handler.py, formats the responses and returns the results to DialogFlow. 

The handler.py file contains functions with API calls. When a user starts interacting, we save their fb_id (not their personal information, just a large integer) to session storage. This allows us to serve relevant information, in this case, doctors covered by their insurance. 


