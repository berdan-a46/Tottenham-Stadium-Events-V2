from django.http import HttpResponse
import json
import heapq
from datetime import datetime
from scripts.tottenhamFootballMen import tottenhamFootballMen
from scripts.rugbyAndTMEvents import rugbyAndTMEvents

def parseDate(event):
    date = event[2]  
    time = event[3] 
    dateTime = f"{date} {time}"
    return datetime.strptime(dateTime, "%A %d %B %Y %H:%M")

def index(request):
    eventDictionary = {}
    eventDictionary["rugby"], eventDictionary["ticketMasterTottenham"] = rugbyAndTMEvents()
    eventDictionary["tottenhamFootballMen"] = tottenhamFootballMen()
     
    minHeap = []
    result = []

    #Push first event of each event type into the heap to start it off
    for eventType, eventList in eventDictionary.items():
        if eventList:
            firstEvent = eventList[0]
            firstEventDate = parseDate(firstEvent)
            heapq.heappush(minHeap, (firstEventDate, firstEvent, 0, eventList))

    while minHeap:
        currentDate, currentEvent, index, eventList = heapq.heappop(minHeap)
        result.append(currentEvent)

        
        if index + 1 < len(eventList):
            nextEvent = eventList[index + 1]
            nextEventDate = parseDate(nextEvent)
            heapq.heappush(minHeap, (nextEventDate, nextEvent, index + 1, eventList))
    
    return HttpResponse(json.dumps(result))

