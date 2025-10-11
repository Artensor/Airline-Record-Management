import { formSubmit } from "../js/add_new_clients_form.js";

let fetch_args;
window.fetch = async (url, options) => {
    fetch_args = [url, options];
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


async function testAddNewClients(log) {
  const mockEvent = {
    preventDefault: () => console.log("preventDefault called"),
    target: mockForm,
  };

  await formSubmit(mockEvent);

  const [url, options] = fetch_args || [];

  console.assert(url === "http://127.0.0.1:5000/api/v1/clients", "Wrong URL used in fetch");
  console.assert(options.method === "POST", "Method should be POST");
  console.assert(options.headers["Content-type"] === "application/json", "Missing JSON header");
  console.assert(JSON.parse(options.body).name === "Jane Doe", "Client name not sent correctly");

  log("testAddNewClients passed");
  alert("testAddNewClients passed");
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

export async function runAllTests(results) {
    const log = (item) => {
        const child = document.createElement("p");
        child.innerText = item;
        results.appendChild(child);
    }

    testAddNewClients(log);
}


