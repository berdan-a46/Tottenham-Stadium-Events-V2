import requests
import os
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

apiKey = os.environ.get("TM_API_KEY")
if not apiKey:
    raise RuntimeError("TM_API_KEY not set")

def isAlreadySameDateAndTime(eventArray, currentEvent):
    for event in eventArray:
         if event[1] == currentEvent['dates']['start']["localDate"] and event[2] == event['dates']['start']["localTime"]:
              return True
    return False

def isUpcoming(event):
    try:
        eventDate = datetime.strptime(
            event['dates']['start']["localDate"], "%Y-%m-%d"
        ).date()
    except Exception as e:
        print("date parse failed:", e)

    today = datetime.now(timezone.utc).date()
    return eventDate >= today


def formatEvents(events):
    formattedEvents = []
    for event in events:
        eventType, name, dateStr, timeStr = event
        dateObj = datetime.strptime(dateStr, "%Y-%m-%d")
        timeObj = datetime.strptime(timeStr, "%H:%M:%S")
        formattedDate = dateObj.strftime("%A %d %B %Y")
        formattedTime = timeObj.strftime("%H:%M")
        formattedEvents.append([eventType,name, formattedDate, formattedTime])
    
    return formattedEvents

def TMEvents():

    url = f'https://app.ticketmaster.com/discovery/v2/events.json?venueId=KovZ9177OxV&apikey={apiKey}'
    response = requests.get(url)
    data = response.json()
    acceptedEvents = []
    if '_embedded' in data:
        events = data['_embedded']['events']
        for event in events:
            if not isAlreadySameDateAndTime(acceptedEvents,event) and isUpcoming(event):
                acceptedEvents.append(["ticketMasterEvent",event["name"], event['dates']['start']["localDate"], event['dates']['start']["localTime"]])
    else:
        print("Failure retrieving")
        print(data)

    formattedEvents = formatEvents(acceptedEvents)


    #Filter out football events from the accepted events
    counter = 0
    tottenhamClubWords = ["tottenham","hotspur","hotspurs","spurs"]
    while counter < len(formattedEvents):
        checkForTottenham = [word for word in tottenhamClubWords if(word in formattedEvents[counter][1].lower())]
        if checkForTottenham:
            formattedEvents.pop(counter)
        else:
            counter +=1

    formattedEvents.sort(key=lambda x: datetime.strptime(f"{x[2]} {x[3]}", "%A %d %B %Y %H:%M"))

    return formattedEvents
