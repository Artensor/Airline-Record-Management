document.addEventListener("DOMContentLoaded", () => {
    const button = document.createElement("button");
    button.textContent = "Click";
    document.body.appendChild(button);

    button.addEventListener("click",() => {
        // //send the request to update the client 
        
        alert("Clicked");
    });
    
});
