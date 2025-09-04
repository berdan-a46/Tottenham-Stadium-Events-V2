from django.http import HttpResponse
import json
import heapq
from datetime import datetime
from scripts.tottenhamFootballMen import tottenhamFootballMen
from scripts.TMEvents import TMEvents
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def parseDate(event):

    date = event[2] if len(event) > 2 else ""
    time = event[3] if len(event) > 3 else ""
    dateTime = f"{date} {time}"

    try:
        return datetime.strptime(dateTime, "%A %d %B %Y %H:%M")
    except ValueError as e:
        raise ValueError(
            f"Failed to parse date/time. date={date!r}, time={time!r}, event={event!r}"
        ) from e

def index(request):
    resp = {"events": []}

    try:
        tmEvents = TMEvents()
        resp["ticketMasterTottenham"] = tmEvents
    except Exception as e:
        logger.exception("TMEvents failed")
        resp["ticketMasterTottenham"] = []
        resp["tm_error"] = str(e)

    try:
        spursEvents = tottenhamFootballMen()
        resp["tottenhamFootballMen"] = spursEvents
    except Exception as e:
        logger.exception("tottenhamFootballMen failed")
        resp["tottenhamFootballMen"] = []
        resp["spurs_error"] = str(e)

    return JsonResponse(resp)

def indexOld(request):
    eventDictionary = {}
    tm_events = TMEvents()
    spurs_events = tottenhamFootballMen()


    eventDictionary["ticketMasterTottenham"] = tm_events
    eventDictionary["tottenhamFootballMen"] = spurs_events

    minHeap = []
    result = []

    # Push first event of each event type into the heap to start it off
    for eventType, eventList in eventDictionary.items():
        if eventList:
            firstEvent = eventList[0]
            firstEventDate = parseDate(firstEvent)
            heapq.heappush(minHeap, (firstEventDate, firstEvent, 0, eventList))

    while minHeap:
        currentDate, currentEvent, index_in_list, eventList = heapq.heappop(minHeap)
        result.append(currentEvent)

        if index_in_list + 1 < len(eventList):
            nextEvent = eventList[index_in_list + 1]
            nextEventDate = parseDate(nextEvent)
            heapq.heappush(
                minHeap, (nextEventDate, nextEvent, index_in_list + 1, eventList)
            )

    return HttpResponse(json.dumps(result))
