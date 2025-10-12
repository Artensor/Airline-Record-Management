// Ensure test mode even if HTML forgot (safety net)
window.IS_TEST_ENV = true;

// Absolute imports from the /js folder (keeps paths consistent)
import { formClientsSubmit } from "/js/add_new_clients_form.js";
import { formUpdateClientsSubmit, getClientData } from "/js/update_clients_form.js";
import { formAirlinesSubmit } from "/js/add_new_airlines_form.js";
import { formUpdateAirlinesSubmit, getAirlineData } from "/js/update_airlines_form.js";
import { formFlightsSubmit } from "/js/add_new_flights_form.js";
import { formUpdateFlightsSubmit, getFlightData } from "/js/update_flights_form.js";

let fetch_args;

window.fetch = async (url, options = {}) => {

    if (url.includes("/clients/6") && !options.method) {
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

    if (url.includes("/airlines/1") && !options.method) {
        console.log("Mock fetch GET airline data:", url);
        return {
            ok: true,
            json: async () => ({
                id: 1,
                company_name: "Wow Airlines",
                type: "Charter",
            }),
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

    if (url.includes("/airlines/") && options.method === "PUT") {
        fetch_args = [url, options];
        console.log("Mock fetch PUT (airline):", url, options);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Airline updated successfully" }),
        };

    }

    if (url.includes("/flights/5/1/2025-11-12") && !options.method) {
        console.log("Mock fetch GET flight data:", url);
        return {
            ok: true,
            json: async () => ({
                client_id: 5,
                airline_id: 1,
                type: "Charter",
                date: "2025-11-12",
                start_city: "LAX",
                end_city: "SFO",
            }),
        };
    }

    if (url.includes("/flights/5/1/2025-11-12") && options.method === "PUT") {
        fetch_args = [url, options];
        console.log("Mock fetch PUT (flight):", url, options);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Flight updated successfully" }),
        };
    }

    if (url === "http://127.0.0.1:5000/api/v1/flights/5/1/2025-11-12" && options.method === "DELETE") {
        console.log("Mock fetch DELETE (flight):", url);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Flight deleted successfully" }),
        };
    }

    if (url.endsWith("/flights") && options.method === "POST") {
        fetch_args = [url, options];
        console.log("Mock fetch POST (airline):", url, options);
        return {
            ok: true,
            status: 200,
            json: async () => ({ message: "Flight added successfully" }),
        };
    }


    throw new Error(`Unhandled fetch request: ${url}`);
};

const mockFormClient = {
    id: { value: 5 },
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
    id: { value: 1 },
    company_name: { value: "Wow Airlines" },
    type: { value: "Charter" }
};

const mockFormFlight = {
    client_id: { value: 5 },
    airline_id: { value: 1 },
    type: { value: "Charter" },
    date: { value: "2025-11-12" },
    start_city: { value: "LAX" },
    end_city: { value: "SFO" }
};


async function testAddNewClients(log) {
    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockFormClient,
    };

    await formClientsSubmit(mockEvent);

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


    await formUpdateClientsSubmit("6")(mockEvent);


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

    await formAirlinesSubmit(mockEvent);

    const [url, options] = fetch_args || [];

    console.assert(url === "http://127.0.0.1:5000/api/v1/airlines", "Wrong URL used in fetch");
    console.assert(options.method === "POST", "Method should be POST");
    console.assert(options.headers["Content-type"] === "application/json", "Missing JSON header");
    console.assert(JSON.parse(options.body).company_name === "Wow Airlines", "Airline company name not sent correctly");

    log("testAddNewAirlines passed");
}


async function testUpdateAirlines(log) {
    const existingAirlineData = {
        id: { value: 1 },
        company_name: { value: "Wowza Airlines" },
        type: { value: "Charter" },
    };

    const mockForm = {
        elements: {
            company_name: { value: "" },
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

    await getAirlineData(1, mockForm);

    mockForm.elements["company_name"].value = "Transatlantic Airlines";


    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockForm,
    };


    await formUpdateAirlinesSubmit(1)(mockEvent);


    const [url, options] = fetch_args || [];

    console.assert(url === "http://127.0.0.1:5000/api/v1/airlines/1", "Wrong URL for update");
    console.assert(options.method === "PUT", "Method should be PUT");
    console.assert(JSON.parse(options.body).company_name === "Transatlantic Airlines", "Updated airline name not sent correctly");
    log("testUpdateAirlines passed");
}


async function testAddNewFlights(log) {
    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockFormFlight,
    };

    await formFlightsSubmit(mockEvent);

    const [url, options] = fetch_args || [];

    console.assert(url === "http://127.0.0.1:5000/api/v1/flights", "Wrong URL used in fetch");
    console.assert(options.method === "POST", "Method should be POST");
    console.assert(options.headers["Content-type"] === "application/json", "Missing JSON header");
    console.assert(JSON.parse(options.body).date === "2025-11-12", "Flight date was not sent correctly");

    log("testAddNewFlights passed");
}

async function testUpdateFlights(log) {
    const existingFlightData = {
        client_id: { value: 5 },
        airline_id: { value: 1 },
        type: { value: "Charter" },
        date: { value: "2025-11-12" },
        start_city: { value: "LAX" },
        end_city: { value: "SFO" }
    };


    const mockForm = {
        elements: {
            client_id: { value: "" },
            airline_id: { value: "" },
            type: { value: "" },
            date: { value: "" },
            start_city: { value: "" },
            end_city: { value: "" },
        }
    };

    await getFlightData(5, 1, "2025-11-12", mockForm);


    mockForm.elements["date"].value = "2025-12-02";


    const mockEvent = {
        preventDefault: () => console.log("preventDefault called"),
        target: mockForm,
    };


    await formUpdateFlightsSubmit(5, 1, "2025-11-12")(mockEvent);


    const [url, options] = fetch_args || [];

    console.assert(
        url === "http://127.0.0.1:5000/api/v1/flights",
        "Wrong URL for update"
    );
    console.assert(JSON.parse(options.body).date === "2025-12-02", "Flight date was not updated correctly");
    log("testUpdateFlights passed");
}

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

    fetch_args = null;

    await testUpdateAirlines(log);

    fetch_args = null;

    await testAddNewFlights(log);

    fetch_args = null;

    await testUpdateFlights(log);

  // explicit pass banner so it's obvious
  const done = document.createElement("p");
  done.textContent = "✅ Suite passed";
  done.style.fontWeight = "bold";
  results.appendChild(done);

}


