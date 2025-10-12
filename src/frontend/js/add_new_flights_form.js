export async function formFlightSubmit(event) {
    event.preventDefault();

    const flightData = {
        client_id: Number(event.target["client_id"].value),
        airline_id: Number(event.target["airline_id"].value),
        date: event.target["date"].value,
        start_city: event.target["start_city"].value,
        end_city: event.target["end_city"].value,
    }
    //send the request to create the client
    try {
        const res = await fetch(`http://127.0.0.1:5000/api/v1/flights`, {
            method: "POST",
            headers: { "Content-type": "application/json" },
            body: JSON.stringify(flightData)
        });

        const data = await res.json();

        console.log("Server response:", data);
        window.location.href = "dashboard.html?tab=flights";
        alert("Submitted");

    } catch (err) {
        console.log("Error:", err);
    }

}

