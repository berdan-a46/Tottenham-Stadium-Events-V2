import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Event from './components/Event';

function App() {
  const [events, setEvents] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchEvents();
  }, []);
  
  /*
  Fetch events from events.json file. Prevent caching to prevent old data from being presented.
  Set the events list, handle loaded state, and any errors
  */
  const fetchEvents = async () => {
    setLoaded(false);
    setError(null);

    try {
      const response = await axios.get('/data/events.json', {
        headers: { 'Cache-Control': 'no-cache' },
      });
      const payload = response.data || {};
      const list = Array.isArray(payload.events) ? payload.events : [];
      setEvents(list);
      console.log(list)
    } catch (error) {
      console.error('Error fetching events.json:', error);
      setError(error);
    } finally{
      setLoaded(true);
    }
  };


  return (
    <>
      <div className="event-header">
        <h2>Tottenham Hotspur Stadium Events</h2>

        {/* Show loading bar and any error messages */}
        <div className="refresh-container" style={{ textAlign: 'center' }}>
          {!loaded && <div className="loading-bar"></div>}
          {error && <p className="error">Error: {error.message}</p>}
        </div>

        {/* Render events once data is loaded */}
        <div className="event-container">
          {loaded &&
            events.map((event, index) => (
              <div key={index} className="event-box-wrapper">
                <Event
                  name={event[1]}
                  abbreviations={
                    event[0].includes('Football') ? [event[4][0], event[4][1]] : undefined
                  }
                  date={event[2]}
                  time={event[3]}
                  tag={event[0]}
                />
              </div>
            ))}
        </div>
      </div>
    </>
  );
}

export default App;
