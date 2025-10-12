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

//submit handler for updating a client
export const formUpdateClientsSubmit = (id) => async (event) => {
    event.preventDefault();
    const form = event.target;

    //build updated client payload
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

    try {
        //send the request to update the client
        const res = await fetch(`http://127.0.0.1:5000/api/v1/clients/${id}`, {
            method: "PUT",
            headers: { "Content-type": "application/json" },
            body: JSON.stringify(updatedClient)
        });

        //check if request was successful
        if (!res.ok) {
            let errText = `update failed (status ${res.status})`;
            try {
                const errJson = await res.json();
                if (errJson && errJson.error) errText = `update failed: ${errJson.error}`;
            } catch { /* ignore parse errors */ }
            alert(errText);
            return;
        }

        //show success message and redirect back to clients dashboard (only outside test runner)
        if (!window.IS_TEST_ENV) {
            alert("submitted");
            window.location.href = "/?tab=clients";
        }

    } catch (e) {
        //handle network error
        console.error("network error:", e);
        if (!window.IS_TEST_ENV) {
            alert("network error — please try again.");
        }
    }
}