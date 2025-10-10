
//get all data and fill the update form
async function getRecordData(id, form) {

    if (id) {

        fetch(`http://127.0.0.1:5000/api/v1/airlines/${id}`)
            .then(res => res.json())
            .then(airline => {
                form.elements["company_name"].value = airline.company_name || "";
                form.elements["type"].value = airline.type || "";
            })

    }

}

const formSubmit = (id) => async (event) =>  {
    event.preventDefault();
    const form = event.target;

    //updates inputs
    const updatedAirline = {
        company_name: form.elements["company_name"].value,
        type: form.elements["type"].value,
    };


    //send the request to update the airline
    fetch(`http://127.0.0.1:5000/api/v1/airlines/${id}`, {
        method: "PUT",
        headers: { "Content-type": "application/json" },
        body: JSON.stringify(updatedAirline)
    })
    window.location.href = "dashboard.html?tab=airlines";
    alert("Submitted");
};


document.addEventListener("DOMContentLoaded", () => {

    //get form from the page
    const form = document.getElementById("update_airlines_form")

    // get record params from the url
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    getRecordData(id, form);
    form.addEventListener("submit", formSubmit(id));
});
