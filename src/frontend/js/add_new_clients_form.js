//submit handler for add new client
export async function formClientsSubmit(event) {
  event.preventDefault();

  //collect inputs
  const clientData = {
    id: Number(event.target["id"].value),
    name: event.target["name"].value,
    type: event.target["type"].value,
    phone_number: event.target["phone_number"].value,
    address_line1: event.target["address_line1"].value,
    address_line2: event.target["address_line2"].value,
    address_line3: event.target["address_line3"].value,
    city: event.target["city"].value,
    state: event.target["state"].value,
    zip_code: event.target["zip_code"].value,
    country: event.target["country"].value
  };

  //send the request to create the client
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/v1/clients`, {
      method: "POST",
      headers: { "Content-type": "application/json" },
      body: JSON.stringify(clientData)
    });

    //optional: inspect response for debugging
    const data = await res.json();
    console.log("Server response:", data);

    // success UX — only when not running inside the test harness
    if (!window.IS_TEST_ENV) {
      alert("Submitted");
      // use absolute path so it works from any page (e.g. /tests/)
      window.location.href = "/?tab=clients";
    }

  } catch (err) {
    console.log("Error:", err);
    if (!window.IS_TEST_ENV) {
      alert("Network error — please try again.");
    }
  }
}