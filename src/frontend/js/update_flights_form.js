//get all data and fill the update form
export async function getFlightData(client_id, airline_id, date, form) {

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

export const formUpdateFlightsSubmit = (client_id, airline_id, old_date) => async (event) => {
    event.preventDefault();
    const form = event.target;
    const new_date = form.elements["date"].value;

    const updatedFlight = {
        date: new_date,
        start_city: form.elements["start_city"].value,
        end_city: form.elements["end_city"].value,
    };


    if (new_date !== old_date) {
        await fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${old_date}`, {
            method: "DELETE"
        });

        await fetch(`http://127.0.0.1:5000/api/v1/flights`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                client_id,
                airline_id,
                date: new_date,
                start_city: updatedFlight.start_city,
                end_city: updatedFlight.end_city
            })
        });
    } else {
        await fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${old_date}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updatedFlight)
        });
    }
}


