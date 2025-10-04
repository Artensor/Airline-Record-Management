document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("edit_form")

    

    form.addEventListener("submit",() => {
        //send the request to update the client
        fetch(`http://127.0.0.1:5000//api/v1/clients/${document.getElementById}`,{
            method: "PUT",
            headers: {"Content-type": "application/json"}
        })
        
        alert("Submitted");
    });
    
});
