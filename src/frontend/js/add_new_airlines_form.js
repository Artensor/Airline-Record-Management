async function formSubmit(event) {
    event.preventDefault();

    const airlineData = {
        id: event.target["id"].value,
        company_name: event.target["company_name"].value,
        type: event.target["type"].value,
    }
    //send the request to update the client
    try {
        const res = await fetch(`http://127.0.0.1:5000/api/v1/airlines`, {
            method: "POST",
            headers: { "Content-type": "application/json" },
            body: JSON.stringify(airlineData)
        });

        const data = await res.json();

        console.log("Server response:", data);
        window.location.href = "dashboard.html?tab=airlines";
        alert("Submitted");

    } catch (err) {
        console.log("Error:", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("add_new_airlines_form")
    form.addEventListener("submit", formSubmit);
});

