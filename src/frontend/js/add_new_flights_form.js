async function formSubmit(event) {
    event.preventDefault();

    const flightData = {
        client_id: event.target["client_id"].value,
        airline_id: event.target["airline_id"].value,
        date: event.target["date"].value,
        start_city: event.target["start_city"].value,
        end_city: event.target["end_city"].value,
    }
    //send the request to update the client
    try {
        const res = await fetch(`http://127.0.0.1:5000/api/v1/flights`, {
            method: "POST",
            headers: { "Content-type": "application/json" },
            body: JSON.stringify(clientData)
        });

        const data = await res.json();

        console.log("Server response:", data);
        alert("Submitted");

    } catch (err) {
        console.log("Error:", err);
    }

}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("add_new_flight_form")
    form.addEventListener("submit", formSubmit);
});
