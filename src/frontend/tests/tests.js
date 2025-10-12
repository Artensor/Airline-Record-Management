import { formClientSubmit } from "../js/add_new_clients_form.js";
import { formUpdateClientSubmit, getClientData } from "../js/update_clients_form.js";
import { formAirlineSubmit } from "../js/add_new_airlines_form.js"


let fetch_args;

window.fetch = async (url, options) => {
    if (url.includes("/clients/6") && !options) {
        console.log("Mock fetch GET client data:", url);
        return {
            ok: true,
            json: async () => ({
                id: 6,
                name: "Jane Doe",
                type: "Business",
                phone_number: "+15555555555",
                address_line1: "123 Main St",
                address_line2: "",
                address_line3: "",
                city: "New York",
                state: "NY",
                zip_code: "10001",
                country: "USA",
            }),
        };
    }

    if (url.endsWith("/clients") && options.method === "POST") {
        fetch_args = [url, options];
        console.log("Mock fetch POST:", url, options);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Client added successfully" }),
        };
    }

    if (url.includes("/clients/6") && options.method === "PUT") {
        fetch_args = [url, options];
        console.log("Mock fetch PUT:", url, options);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Client updated successfully" }),
        };
    }
    if (url.endsWith("/airlines") && options.method === "POST") {
        fetch_args = [url, options];
        console.log("Mock fetch POST (airline):", url, options);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Airline added successfully" }),
        };
    }


    throw new Error(`Unhandled fetch request: ${url}`);
};

const mockFormClient = {
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

const mockFormAirline = {
    id: { value: "1" },
    company_name: { value: "Wow Airlines" },
    type: { value: "Charter" }
};

const mockFormFlight = {
    client_id: { value: 5 },
    airline_id: { value: 1 },
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
        target: mockFormClient,
    };

    await formClientSubmit(mockEvent);

    const [url, options] = fetch_args || [];

    console.assert(url === "http://127.0.0.1:5000/api/v1/clients", "Wrong URL used in fetch");
    console.assert(options.method === "POST", "Method should be POST");
    console.assert(options.headers["Content-type"] === "application/json", "Missing JSON header");
    console.assert(JSON.parse(options.body).name === "Jane Doe", "Company name was not sent correctly");

    log("testAddNewClients passed");
}


async function testUpdateClients(log) {
    const existingClientData = {
        id: 6,
        name: "Jane Doe",
        type: "Business",
        phone_number: "+15555555555",
        address_line1: "123 Main St",
        address_line2: "",
        address_line3: "",
        city: "New York",
        state: "NY",
        zip_code: "10001",
        country: "USA",
    };

    const mockForm = {
        elements: {
            name: { value: "" },
            type: { value: "" },
            phone_number: { value: "" },
            address_line1: { value: "" },
            address_line2: { value: "" },
            address_line3: { value: "" },
            city: { value: "" },
            state: { value: "" },
            zip_code: { value: "" },
            country: { value: "" },
        }
    };

    await getClientData(6, mockForm);

    mockForm.elements["name"].value = "Karina Rodriguez";


    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockForm,
    };


    await formUpdateClientSubmit("6")(mockEvent);


    const [url, options] = fetch_args || [];

    console.assert(url === "http://127.0.0.1:5000/api/v1/clients/6", "Wrong URL for update");
    console.assert(options.method === "PUT", "Method should be PUT");
    console.assert(JSON.parse(options.body).name === "Karina Rodriguez", "Updated name not sent correctly");

    log("testUpdateClients passed");
}

async function testAddNewAirlines(log) {
    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockFormAirline,
    };

    await formAirlineSubmit(mockEvent);

    const [url, options] = fetch_args || [];

    console.assert(url === "http://127.0.0.1:5000/api/v1/airlines", "Wrong URL used in fetch");
    console.assert(options.method === "POST", "Method should be POST");
    console.assert(options.headers["Content-type"] === "application/json", "Missing JSON header");
    console.assert(JSON.parse(options.body).company_name === "Wow Airlines", "Airline company name not sent correctly");

    log("testAddNewAirlines passed");
}


// async function testUpdateAirlines() {
//     const existingAirlineData = {
//         id: 6,
//         name: "Jane Doe",
//         type: "Business",
//         phone_number: "+15555555555",
//         address_line1: "123 Main St",
//         address_line2: "",
//         address_line3: "",
//         city: "New York",
//         state: "NY",
//         zip_code: "10001",
//         country: "USA",
//     };

//     const mockForm = {
//         elements: {
//             name: { value: "" },
//             type: { value: "" },
//             phone_number: { value: "" },
//             address_line1: { value: "" },
//             address_line2: { value: "" },
//             address_line3: { value: "" },
//             city: { value: "" },
//             state: { value: "" },
//             zip_code: { value: "" },
//             country: { value: "" },
//         }
//     };

//     await getClientData(6, mockForm);

//     mockForm.elements["name"].value = "Karina Rodriguez";


//     const mockEvent = {
//         preventDefault: () => console.log("preventDefault called"),
//         target: mockForm,
//     };


//     await formUpdateAirlinesSubmit("6")(mockEvent);


//     const [url, options] = fetch_args || [];

//     console.assert(url === "http://127.0.0.1:5000/api/v1/airlines/6", "Wrong URL for update");
//     console.assert(options.method === "PUT", "Method should be PUT");
//     console.assert(JSON.parse(options.body).name === "Karina Rodriguez", "Updated name not sent correctly");

//     log("testUpdateClients passed");
// }


// function testAddNewFlights() {
//     if (true) {

//     }


//     // console.assert();
// }

// function testUpdateFlights() {

//     if (true) {

//     }


//     // console.assert();
// }

// function testDeleteRecord() {

//     if (true) {

//     }


//     // console.assert();

// }


// function testDashboardTable() {

//     if (true) {

//     }


//     // console.assert();

// }

export async function runAllTests(results) {
    const log = (item) => {
        const child = document.createElement("p");
        child.innerText = item;
        results.appendChild(child);
    }

    await testAddNewClients(log);

    fetch_args = null;

    await testUpdateClients(log);

    fetch_args = null;

    await testAddNewAirlines(log);
}


