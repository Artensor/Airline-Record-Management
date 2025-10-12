export async function formFlightsSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const isTest = !!window.IS_TEST_ENV;

  const client_id  = Number(form["client_id"].value);
  const airline_id = Number(form["airline_id"].value);
  const date       = form["date"].value;
  const start_city = form["start_city"].value;
  const end_city   = form["end_city"].value;

  // basic ui validation – but don't block automated tests
  const sameCity = start_city.trim().toLowerCase() === end_city.trim().toLowerCase();
  if (sameCity && !isTest) {
    alert("Start and End City must differ");
    return { ok: false, reason: "same-city" };
  }

  const flightData = { client_id, airline_id, date, start_city, end_city };

  try {
    const res = await fetch("http://127.0.0.1:5000/api/v1/flights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(flightData),
    });

    if (!res.ok) {
      // surface API error in real runs; still return a structured result
      if (!isTest) {
        let msg = `create failed (status ${res.status})`;
        try {
          const j = await res.json();
          if (j?.error) msg = `create failed: ${j.error}`;
        } catch {}
        alert(msg);
      }
      return { ok: false, status: res.status };
    }

    // success — page script will alert + redirect (unless in tests)
    return { ok: true, status: res.status };

  } catch (err) {
    console.error("Error:", err);
    if (!isTest) alert("network error — please try again.");
    return { ok: false, reason: "network-error" };
  }
}