import json
import heapq
from datetime import datetime
from tottenhamFootballMen import tottenhamFootballMen
from TMEvents import TMEvents
import logging
from django.http import JsonResponse
import time
from pathlib import Path

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


def runAllScripts():
    eventDictionary = {}
    tmEvents = TMEvents()
    spursEvents = tottenhamFootballMen()


    eventDictionary["ticketMasterTottenham"] = tmEvents
    eventDictionary["tottenhamFootballMen"] = spursEvents

    minHeap = []
    result = []

    # Push first event of each event type into the heap to start it off
    for eventType, eventList in eventDictionary.items():
        if eventList:
            firstEvent = eventList[0]
            firstEventDate = parseDate(firstEvent)
            heapq.heappush(minHeap, (firstEventDate, firstEvent, 0, eventList))

    # Continuously pop the earliest event and push the next from the same list
    while minHeap:
        currentDate, currentEvent, indexInList, eventList = heapq.heappop(minHeap)
        result.append(currentEvent)

        if indexInList + 1 < len(eventList):
            nextEvent = eventList[indexInList + 1]
            nextEventDate = parseDate(nextEvent)
            heapq.heappush(
                minHeap, (nextEventDate, nextEvent, indexInList + 1, eventList)
            )

    return result


if __name__ == "__main__":
    events = runAllScripts()
    out_path = Path("frontend/public/data/events.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "updated_at": int(time.time()),
        "events": events
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    