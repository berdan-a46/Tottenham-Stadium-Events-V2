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

#Sometimes ticketmaster api returns duplicate events. Use this helper function to filter out these events
def dedupeEvents(events):
    eventsDictionary = {}

    for event in events:
        eventType, name, dateStr, timeStr = event
        key = (dateStr, timeStr)

        if key not in eventsDictionary:
            eventsDictionary[key] = event
        else:
            # Compare the duplicates. Keep the one with a shorter name
            existingEvent = eventsDictionary[key]
            if len(name) < len(existingEvent[1]):
                eventsDictionary[key] = event

    # Convert dictionary back to a list of events
    dedupedEvents = list(eventsDictionary.values())
    return dedupedEvents

"""
Helper function to filter out events that may have passed.
Need this because sometimes when api is called at scheduled time by CRON job, api hasn't yet removed an event
that has just passed.
"""
def isUpcoming(event):
    try:
        eventDate = datetime.strptime(
            event['dates']['start']["localDate"], "%Y-%m-%d"
        ).date()
    except Exception as e:
        print("date parse failed:", e)
        return False

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
            if isUpcoming(event):
                acceptedEvents.append(["ticketMasterEvent",event["name"], event['dates']['start']["localDate"], event['dates']['start']["localTime"]])
    else:
        print("Failure retrieving")
        print(data)


    formattedEvents = formatEvents(dedupeEvents(acceptedEvents))


    #Filter out football events from the accepted events so they aren't duplicated with the Spurs fixtures
    counter = 0
    tottenhamClubWords = ["tottenham","hotspur","hotspurs","spurs"]
    while counter < len(formattedEvents):
        checkForTottenham = [word for word in tottenhamClubWords if(word in formattedEvents[counter][1].lower())]
        if checkForTottenham:
            formattedEvents.pop(counter)
        else:
            counter +=1

    #Sort chronologically by datetime
    formattedEvents.sort(key=lambda x: datetime.strptime(f"{x[2]} {x[3]}", "%A %d %B %Y %H:%M"))

    return formattedEvents
