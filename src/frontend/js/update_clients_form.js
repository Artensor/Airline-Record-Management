document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("update_client_form")
    
    //get record params from the url
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");


    //get all the filled data
    if(id){
        fetch(`http://127.0.0.1:5000/api/v1/clients/${id}`)
        .then(res => res.json)
        .then( client => {
            form.elements["name"].value = client.name || "";
            form.elements["type"].value = client.type || "";
            form.elements["phone_number"].value = client.phone_number || ""; 
        })

    }

    form.addEventListener("submit",() => {
        
        const id = document.getElementById("id").value;

        //send the request to update the client
        fetch(`http://127.0.0.1:5000/api/v1/clients/${id}`,{
            method: "PUT",
            headers: {"Content-type": "application/json"}
        })
        
        alert("Submitted");
    });
    
});
