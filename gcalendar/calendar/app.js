fetch("/api/events")
  .then(res => res.json())
  .then(events => {
    console.log(events);
    // zde bys naplnil FullCalendar UI
  });
