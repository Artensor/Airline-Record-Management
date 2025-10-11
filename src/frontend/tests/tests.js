
window.fetch = async () => {
    console.log("Mock fetch called with:", url, options);

    return {
        ok: true,
        status: 200,
        json: async () => ({
            data: [
                { id: 1, name: "Caro Diaz", type: "Business", phone_number: "+15555555555", address_line1: "123 Live St.", city: "Smallville", state: "CA", zip_code: "12345" },
                { id: 2, name: "Natalie Diaz", type: "Business", phone_number: "+14444444444", address_line1: "234 Liven St.", city: "Funville", state: "CA", zip_code: "54678" }
            ]
        })
    };
}

function testAddNewClients() {
    if (true) {

    }


    console.assert();
}

function testUpdateClients() {

    if (true) {

    }


    console.assert();
}


function testAddNewAirlines() {
    if (true) {

    }


    console.assert();
}

function testUpdateAirlines() {

    if (true) {

    }


    console.assert();
}


function testAddNewFlights() {
    if (true) {

    }


    console.assert();
}

function testUpdateFlights() {

    if (true) {

    }


    console.assert();
}


function testDashboardTable() {

    if (true) {

    }


    console.assert();
}