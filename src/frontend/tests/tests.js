import { formSubmit } from "../js/add_new_clients_form.js";

window.fetch = async (url, options) => {
    console.log("Mock fetch called with:", url, options);

    return {
        ok: true,
        status: 200,
        json: async () => ({ message: "Client added successfully" }),
    };
}

const mockForm = {
    id: { value: "5" },
    name: { value: "Jane Doe" },
    type: { value: "Business" },
    phone_number: { value: "+15555555555" },
    address_line1: { value: "123 Main St" },
    address_line2: { value: "" },
    address_line3: { value: "" },
    city: { value: "New York" },
    state: { value: "NY" },
    zip_code: { value: "10001" },
    country: { value: "USA" },
};

async function testAddNewClients() {
    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockForm,
    };

    await formSubmit(mockEvent);

    console.assert(
        output.some(line => line.includes("Mock fetch called with")),
        "fetch was not called"
    );
    console.assert(
        output.some(line => line.includes("Submitting client")),
        "formSubmit did not log submission"
    );

    alert("testAddNewClients passed");


    console.log = originalLog;
}

// function testUpdateClients() {

//     if (true) {

//     }


//     console.assert();
// }


// function testAddNewAirlines() {
//     if (true) {

//     }


//     console.assert();
// }

// function testUpdateAirlines() {

//     if (true) {

//     }


//     console.assert();
// }


// function testAddNewFlights() {
//     if (true) {

//     }


//     console.assert();
// }

// function testUpdateFlights() {

//     if (true) {

//     }


//     console.assert();
// }


// function testDashboardTable() {

//     if (true) {

//     }


//     console.assert();

// }


// Run the test automatically
testAddNewClients();