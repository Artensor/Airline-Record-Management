document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("update_client_form")

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
