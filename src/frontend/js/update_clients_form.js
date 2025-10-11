
//get all data and fill the update form
export async function getClientData(id, form) {

    if (id) {

        fetch(`http://127.0.0.1:5000/api/v1/clients/${id}`)
            .then(res => res.json())
            .then(client => {
                form.elements["name"].value = client.name || "";
                form.elements["type"].value = client.type || "";
                form.elements["phone_number"].value = client.phone_number || "";
                form.elements["address_line1"].value = client.address_line1 || "";
                form.elements["address_line2"].value = client.address_line2 || "";
                form.elements["address_line3"].value = client.address_line3 || "";
                form.elements["city"].value = client.city || "";
                form.elements["state"].value = client.state || "";
                form.elements["zip_code"].value = client.zip_code || "";
                form.elements["country"].value = client.country || "";
            })

    }

}

export const formUpdateClientSubmit = (id) => async (event) => {
    event.preventDefault();
    const form = event.target;

    //updates inputs
    const updatedClient = {
        name: form.elements["name"].value,
        type: form.elements["type"].value,
        phone_number: form.elements["phone_number"].value,
        address_line1: form.elements["address_line1"].value,
        address_line2: form.elements["address_line2"].value,
        address_line3: form.elements["address_line3"].value,
        city: form.elements["city"].value,
        state: form.elements["state"].value,
        zip_code: form.elements["zip_code"].value,
        country: form.elements["country"].value
    };


    //send the request to update the client
    fetch(`http://127.0.0.1:5000/api/v1/clients/${id}`, {
        method: "PUT",
        headers: { "Content-type": "application/json" },
        body: JSON.stringify(updatedClient)
    })

}
