document.addEventListener("DOMContentLoaded", () => {
  const headings = {
    clients: [{ label: "ID", key: "id" }, { label: "Type", key: "type" }, { label: "Name", key: "name" }, { label: "Address Line 1", key: "adress_line2" }, { label: "Address Line 2", key: "adress_line3" }, { label: "Address Line 3", key: "adress_line1" }, { label: "City", key: "city" }, { label: "State", key: "state" }, { label: "Country", key: "country" }, { label: "Phone", key: "phone_numnber" }, { label: "Actions" }],
    flights: [{ label: "Client", key: "client_id" }, { label: "Airline", key: "airline_id" }, { label: "date", key: "date" }, { label: "Start City", key: "start_city" }, { label: "End City", key: "end_city" }, { label: "Acitions" }],
    airlines: [{ label: "Company Name", key: "company_name" }, { label: "Actions", key: "actions" }]
  }


  const tabs = document.querySelectorAll(".tab")

  const contents = document.querySelectorAll(".tab-content")

  //removes active class from all tab buttons and adds hidden class to their content
  function resetTabs() {
    tabs.forEach(tab => tab.classList.remove("active"));
    contents.forEach(content => content.classList.add("hidden"));
  }

  tabs.forEach(tab => {
    tab.addEventListener("click", async () => {

      const type = tab.dataset.type;
      const endpoint = tab.dataset.endpoint;
      //get the div container content of the selected tab with the id
      const selectedTabContent = document.getElementById(tab.dataset.tab)

      resetTabs();

      //updates active tab
      tab.classList.add("active");
      selectedTabContent.classList.remove("hidden");

      //update url with selected tab params
      const url = new URL(window.location.href);
      url.searchParams.set("tab", type);
      window.history.pushState(null, '', url.toString());

      //fetch data for tab data table
      try {
        const res = await fetch(`http://127.0.0.1:5000${endpoint}`);

        const data = await res.json();

        const tableHeadings = headings[type];

        selectedTabContent.innerHTML = table(data, tableHeadings, type);

        console.log("Server response:", data);

      } catch (err) {
        console.log("Error:", err);
      }

    })

    async function deleteRecord(type, id) {

    }

    //builds the table for each tab record selected
    function table(data, tableHeadings, type) {
      const headerRow = tableHeadings.map(h => `<th>${h.label}</th>`).join("");
      const bodyRows = data.data.map(item =>
        `<tr>
    ${tableHeadings.map(h => {
          if (!h.key) {
            return `<td><a href="update_${type}_form.html?id=${item.id}">Edit</a>
        <button onclick="deleteRecord('${type}', '${item.id}')">Delete</button></td>`
          }
          else {
            return `<td>${item[h.key] ?? ""}</td>`

          }
        }).join("")}
    
    </tr>`
      ).join("");

      return `
    <table border="1">
      <thead><tr>${headerRow}</tr></thead>
      <tbody>${bodyRows}</tbody>
    </table>
  `;
    }
  });
})