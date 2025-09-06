# Tottenham Stadium Events (V2)

### Project Overview
This project was inspired by a real-world problem: a family member unfamiliar with English and technology struggled to find event schedules for the Spurs Stadium. To address this, I built an automated system that collects and displays all events hosted at the stadium in one place.

This is an updated version of my original Tottenham Stadium Events project.<br>
The goal was to simplify hosting, reduce dependencies, and make the project easier to maintain.<br>
This version removes the Django backend in favor of a lightweight pipeline: Python scripts generate a static events.json file, which a React frontend uses. <br>

### Improvements Since V1
- No Django backend - Replaced with JSON generation + static serving.
   - Significantly improves the fetching speed.
- Improved filtering for Ticketmaster API.
 
### How It Works
- Python scripts
  - Fetch Ticketmaster events via API.
  - Scrape Spurs fixtures via Selenium.
  - Normalize, de-dupe, and merge events into a single list.
  - Write results to /web/public/data/events.json.

- React frontend
  - Reads the static JSON file.
  - Displays all upcoming events with date, time, and tags.
  - Handles any errors that may arise with fetching the data.

### Tech Stack
- Python
- Selenium
- React
- Ticketmaster Discovery API
- CRON
