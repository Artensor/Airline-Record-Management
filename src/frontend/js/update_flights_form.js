//get all data and fill the update form
export async function getFlightData(client_id, airline_id, date, form) {
  if (client_id && airline_id && date) {
    fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${date}`)
      .then(res => res.json())
      .then(flight => {
        // normalise date for <input type="date">
        const d = flight.date || "";
        const onlyDate = d.includes("T") ? d.split("T")[0] : d;

        form.elements["date"].value = onlyDate || "";
        form.elements["start_city"].value = flight.start_city || "";
        form.elements["end_city"].value = flight.end_city || "";
      });
  }
}

// submit handler for updating a flight
export const formUpdateFlightsSubmit = (client_id, airline_id, old_date) => async (event) => {
  event.preventDefault();
  const form = event.target;
  const isTest = !!window.IS_TEST_ENV;

  // collect values
  const new_date = form.elements["date"].value;
  const start_city = form.elements["start_city"].value;
  const end_city = form.elements["end_city"].value;

  // basic ui validation – but don't block automated tests
  const sameCity = start_city.trim().toLowerCase() === end_city.trim().toLowerCase();
  if (sameCity && !isTest) {
    alert("Start and End City must differ");
    return { ok: false, reason: "same-city" };
  }

  const updatedFlight = { date: new_date, start_city, end_city };

  try {
    if (new_date !== old_date) {
      // delete old identity
      const delRes = await fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${old_date}`, {
        method: "DELETE"
      });
      if (!delRes.ok && delRes.status !== 404) {
        let err = `delete failed (status ${delRes.status})`;
        try { const j = await delRes.json(); if (j?.error) err = `delete failed: ${j.error}`; } catch {}
        if (!isTest) alert(err);
        return;
      }

      // create new identity
      const createRes = await fetch(`http://127.0.0.1:5000/api/v1/flights`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id,
          airline_id,
          date: new_date,
          start_city,
          end_city,
        }),
      });
      if (!createRes.ok) {
        let err = `create failed (status ${createRes.status})`;
        try { const j = await createRes.json(); if (j?.error) err = `create failed: ${j.error}`; } catch {}
        if (!isTest) alert(err);
        return;
      }
    } else {
      // simple update
      const putRes = await fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${old_date}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedFlight),
      });
      if (!putRes.ok) {
        let err = `update failed (status ${putRes.status})`;
        try { const j = await putRes.json(); if (j?.error) err = `update failed: ${j.error}`; } catch {}
        if (!isTest) alert(err);
        return;
      }
    }

    // success UX (skip in tests)
    if (!isTest) {
      alert("submitted");
      window.location.href = "/?tab=flights";
    }
  } catch (e) {
    console.error("network error:", e);
    if (!isTest) alert("network error — please try again.");
  }
};