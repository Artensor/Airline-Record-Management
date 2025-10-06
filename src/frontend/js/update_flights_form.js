document.addEventListener("DOMContentLoaded", () => {

    //get form from the page
    const form = document.getElementById("update_flights_form")

    // get record params from the url
    const params = new URLSearchParams(window.location.search);
    const client_id = params.get("client_id");
    const airline_id = params.get("airline_id");
    const date = params.get("date");

    getRecordData(client_id, airline_id, date);


    //get all data and fill the update form
    async function getRecordData(client_id, airline_id, date) {

        if (client_id && airline_id && date) {

            fetch(`http://127.0.0.1:5000/api/v1/flights/${client_id}/${airline_id}/${date}`)

                .then(res => res.json())
                .then(flight => {
                    form.elements["client_id"].value = flight.client_id || "";
                    form.elements["airline_id"].value = flight.airline_id || "";
                    form.elements["date"].value = flight.date || "";
                    form.elements["start_city"].value = flight.start_city || "";
                    form.elements["end_city"].value = flight.end_city || "";
                })

        }

    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        
        //updates inputs
        const updatedFlight = {
            client_id: form.elements["client_id"].value,
            airline_id: form.elements["airline_id"].value,
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

        alert("Submitted");
    });

});

