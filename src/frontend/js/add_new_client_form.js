document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("add_client_form")


    form.addEventListener("submit",() => {
        //send the request to update the client
        fetch(`http://127.0.0.1:5000//api/v1/clients`,{
            method: "POST",
            headers: {"Content-type": "application/json"}
        })
        
        alert("Submitted");
    });
    
});
