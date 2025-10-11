//get all data and fill the update form
export async function getRecordData(client_id, airline_id, date, form) {

    if (client_id && airline_id && date) {

        fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${date}`)

            .then(res => res.json())
            .then(flight => {
                form.elements["date"].value = flight.date || "";
                form.elements["start_city"].value = flight.start_city || "";
                form.elements["end_city"].value = flight.end_city || "";
            })

    }

}

export const formSubmit = (client_id, airline_id, date) => async (event) => {
    event.preventDefault();
    const form = event.target;

    const updatedFlight = {
        date: form.elements["date"].value,
        start_city: form.elements["start_city"].value,
        end_city: form.elements["end_city"].value,
    };


    //send the request to update the flight
    fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${date}`, {
        method: "PUT",
        headers: { "Content-type": "application/json" },
        body: JSON.stringify(updatedFlight)
    })
    window.location.href = "dashboard.html?tab=flights";
    alert("Submitted");

}

