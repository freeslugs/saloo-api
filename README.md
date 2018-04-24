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

### How to install 

1. Download the source code using `git clone https://github.com/freeslugs/saloo-api`
2. Cd into the `saloo-api` directory.
3. Install requirements `pip install -r requirements.txt`

### How to run 

1. `python app.py`

## How to use 

#### On the browser 

1. Login to `messenger.com` with the username `amanmanik94@gmail.com` and the password `heysaloo123*`
2. Go to `https://www.messenger.com/t/heysaloo123`
3. Start chatting with Saloo

#### On mobile

1. Download the full Facebook messenger app
2. Open the app, login with the username `amanmanik94@gmail.com` and the password `heysaloo123*`
3. Start chatting with Saloo

### Things you can say 

1. Say`Hi` It will respond with generic small talk
2. Ask for a doctor with `find a doctor`; it will ask you for your location
3. Share your location; it will ask you for your insurance provider 
  1. Be sure to enable location sharing privileges 
  2. If you've already shared your location, it'll show you doctors. 
4. Submit your health insurance provider, such as `Aetna`, and it'll list out plans under than provider 
5. Select a health insurance plan, such as `Choice® POS II (Open...`; it will show you doctors for that plan
  1. You can select one of the options from list, or type out the health 

### Known issues

1. Only ask Saloo one question at a time. 
2. Saloo is running on a free instance on Heroku (heroku.com). This means the server goes to sleep when it's not being used. If it doesn't respond, ask it questions again! 
3. There is a bug with Dialogflow which kills requests to the server after 5 seconds. So if a function on the server takes more than five seconds, it won't show the response on messenger.com. This is especially problematic for showing doctors, since we currently scrape `zocdoc.com` and parse through the HTML. I've developed a solution to the problem. When the chatbot has to search for doctors, it first begins an asynchronous function on a separate thread. The server will continously check every second if we have retreved doctors yet. If the results were found, it'll render the results immediately, else it'll prompt you to search for doctors again. This is a known issue, and there is room for improvement, such as integrating directly with their JSON API. 

