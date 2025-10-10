

const headings = {
  clients: [{ label: "ID", key: "id" }, { label: "Type", key: "type" }, { label: "Name", key: "name" }, { label: "Address Line 1", key: "address_line1" }, { label: "Address Line 2", key: "address_line2" }, { label: "Address Line 3", key: "address_line3" }, { label: "City", key: "city" }, { label: "State", key: "state" }, { label: "Country", key: "country" }, { label: "Phone", key: "phone_number" }, { label: "Actions" }],
  flights: [{ label: "Client", key: "client_id" }, { label: "Airline", key: "airline_id" }, { label: "date", key: "date" }, { label: "Start City", key: "start_city" }, { label: "End City", key: "end_city" }, { label: "Actions" }],
  airlines: [{ label: "ID", key: "id" }, { label: "Company Name", key: "company_name" }, { label: "Actions" }]
}

const endpoints = {
  clients: "/api/v1/clients",
  flights: "/api/v1/flights",
  airlines: "/api/v1/airlines"

}

async function deleteRecord(type, id) {
  if (!confirm("Are you sure you want to delete this record?")) {
    return;
  }

  try {
    const res = await fetch(`http://127.0.0.1:5000/api/v1/${type}/${id}`, { method: "DELETE" });
    if (res.ok) {
      alert("Record was deleted.");
      location.reload();
    } else {
      alert("Record wasn't deleted.");
      console.error("Server error:", await res.text());
    }
  } catch (err) {
    console.error("Error:", err);
    alert("An unexpected error occurred.");
  }
}

//removes active class from all tab links and adds hidden class to their content
function resetTabs(tabs, contents) {
  tabs.forEach(tab => tab.classList.remove("active"));
  contents.forEach(content => content.setAttribute("hidden", ""));
}


//fetch data for tab data table
async function fetchTableData(endpoint) {
  try {
    const res = await fetch(`http://127.0.0.1:5000${endpoint}`);
    if (!res.ok) {
      console.error(`Status ${res.status}`);
      return { data: [] };
    }

    const json = await res.json();
    console.log("Response:", json);
    return json;
  } catch (err) {
    console.error("Error:", err);
    return { data: [] };
  }
}


//builds the table for each tab record selected
function table(data, type, tableHeadings) {
  const headerRow = tableHeadings.map(h => `<th>${h.label}</th>`).join("");
  const capitalizedType = type.charAt(0).toUpperCase() + type.slice(1);
  const bodyRows = data.data.map(item => {

    let tableActions = "";

    if (type === "flights") {
      const flightIds = `${item.client_id}/${item.airline_id}/${item.date}`;
      const flightParams = `client_id=${item.client_id}&airline_id=${item.airline_id}&date=${item.date}`;
      tableActions = `
    <td>
      <a href="update_${type}_form.html?${flightParams}">Edit</a>
      <button type="button" onclick="deleteRecord('${type}', '${flightIds}')">Delete</button>
    </td>`;
    } else {
      tableActions = `
    <td>
      <a href="update_${type}_form.html?id=${item.id}">Edit</a>
      <button type="button" onclick="deleteRecord('${type}', '${item.id}')">Delete</button>
    </td>`;
    }

    const cells = tableHeadings.map(h => {
      if (!h.key) { return tableActions }
      else { return `<td>${item[h.key] ?? ""}</td>` }
    }).join("");

    return `<tr>${cells}</tr>`;
  }).join("");


  return `
    <div class="table-wrapper">

    <div class="search-wrapper">
      <div class="table-header"> 
        <h3>${capitalizedType} Management</h3>
      </div>
      
      <form class="search-form">
        <input type="text" name="q" placeholder="Search ${type}..."/>
        <input type="hidden" name="tab" value="${type}">
        <button type="submit">Search</button>
      </form>

      <div class="add-button-wrapper">
        <a href="add_new_${type}_form.html" class="add-new-btn">+ Add New</a>  
      </div> 
    </div>

    <table border="1">

      <thead><tr>${headerRow}</tr></thead>

      <tbody>${bodyRows}</tbody>

      </table>

    </div>
  `;
}


document.addEventListener("DOMContentLoaded", async () => {

  const content = document.getElementById("content");
  const params = new URLSearchParams(window.location.search);
  const type = params.get("tab") || "clients";
  const tableHeadings = headings[type];

  const q = params.get("q") || "";
  const endpoint = `${endpoints[type]}?${new URLSearchParams({ q })}`;
  const data = await fetchTableData(endpoint);
  const html = table(data, type, tableHeadings);
  content.innerHTML = html;

  const tabs = document.querySelectorAll(".tab");
  const contents = document.querySelectorAll(".content");

  resetTabs(tabs, contents);

  //updates active tab
  tabs.forEach(tab => {
    if (tab.dataset.tab == type) { tab.classList.add("active"); }
  })
})