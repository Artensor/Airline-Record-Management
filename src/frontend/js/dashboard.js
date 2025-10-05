

const headings = {
  clients: [{ label: "ID", key: "id" }, { label: "Type", key: "type" }, { label: "Name", key: "name" }, { label: "Address Line 1", key: "adress_line2" }, { label: "Address Line 2", key: "adress_line3" }, { label: "Address Line 3", key: "adress_line1" }, { label: "City", key: "city" }, { label: "State", key: "state" }, { label: "Country", key: "country" }, { label: "Phone", key: "phone_numnber" }, { label: "Actions" }],
  flights: [{ label: "Client", key: "client_id" }, { label: "Airline", key: "airline_id" }, { label: "date", key: "date" }, { label: "Start City", key: "start_city" }, { label: "End City", key: "end_city" }, { label: "Acitions" }],
  airlines: [{ label: "Company Name", key: "company_name" }, { label: "Actions", key: "actions" }]
}

const endpoints = {
  clients: "/api/v1/clients",
  flights: "/api/v1/flights",
  airlines: "/api/v1/airlines"

}

async function deleteRecord(id){
  if(!confirm("Are you sure you want to delete this record?")){
    return;
  } 
   
  const response = await fetch(`http://127.0.0.1:5000/api/v1/clients/${id}`, {method: "DELETE"});

  if(response.ok){
    alert("Record was deleted")
  }else{
    alert("Record wasn't deleted")
  }
}

//removes active class from all tab buttons and adds hidden class to their content
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
  const bodyRows = data.data.map(item =>
    `<tr>
    ${tableHeadings.map(h => {
      if (!h.key) {
        return `<td><a href="update_${type}_form.html?id=${item.id}">Edit</a>
        <button name="id" type="submit" value="${item.id}">Delete</button></td>`
      }
      else {
        return `<td>${item[h.key] ?? ""}</td>`

      }
    }).join("")}
    </tr>`
  ).join("");

  return `
    <div class="table-wrapper">
    <div class="table-header">
    
      <a href="add_new_${type}_form.html" class="add-new-btn">+ Add New</a>
      </div>
      <table border="1">
      <thead><tr>${headerRow}</tr></thead>
      <tbody>${bodyRows}</tbody>
    </table>
    </div>
  `;
}


document.addEventListener("DOMContentLoaded", async () => {

  const content = document.getElementById("content")
  const type = new URLSearchParams(window.location.search).get("tab") || "clients";
  const tableHeadings = headings[type];

  const endpoint = endpoints[type];
  const data = await fetchTableData(endpoint);
  const html = table(data, type, tableHeadings);
  content.innerHTML = html;

  const tabs = document.querySelectorAll(".tab");
  const contents = document.querySelectorAll(".content");
 
  resetTabs(tabs, contents);

  //updates active tab
  tabs.forEach(tab => { tab.classList.add("active"); })
  tabs.forEach(tab => { tab.classList.add("active"); })
  content.removeAttribute("hidden");

  function formSubmitHandler(event){
    const id = event.submitter.value;
    event.preventDefault();
    deleteRecord(id)

  }

  content.addEventListener("submit", formSubmitHandler);

})