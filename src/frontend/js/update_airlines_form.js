//get all data and fill the update form
export async function getAirlineData(id, form) {

    if (id) {
        fetch(`http://127.0.0.1:5000/api/v1/airlines/${id}`)
            .then(res => res.json())
            .then(airline => {
                form.elements["company_name"].value = airline.company_name || "";
                form.elements["type"].value = airline.type || "";
            });
    }

}

//handle the update form submission
export const formUpdateAirlinesSubmit = (id) => async (event) => {
    event.preventDefault();
    const form = event.target;

    //updates inputs
    const updatedAirline = {
        company_name: form.elements["company_name"].value,
        type: form.elements["type"].value
    };

    //send the request to update the airline
    await fetch(`http://127.0.0.1:5000/api/v1/airlines/${id}`, {
        method: "PUT",
        headers: { "Content-type": "application/json" },
        body: JSON.stringify(updatedAirline)
    });

    //show confirmation and redirect back to Airlines table (only outside test runner)
    if (!window.IS_TEST_ENV) {
        alert("Submitted");
        window.location.href = "/dashboard.html?tab=airlines";
    }
};