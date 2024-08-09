document.getElementById("send-btn").addEventListener("click", function() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    appendMessage("user", userInput);
    document.getElementById("user-input").value = "";

    // Send the user input to the backend server
    fetch('http://127.0.0.1:5000/medicalchatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Display the bot's response
        appendMessage("bot", data.reply);
    })
    .catch(error => {
        console.error('Error:', error);
        appendMessage("bot", "There was an error processing your request. Please try again.");
    });
});

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        document.getElementById("send-btn").click();
    }
});

function appendMessage(sender, text) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    const messageContent = document.createElement("div");
    messageContent.classList.add("message-content");
    messageContent.innerText = text;

    messageDiv.appendChild(messageContent);
    document.getElementById("chat-body").appendChild(messageDiv);
    document.getElementById("chat-body").scrollTop = document.getElementById("chat-body").scrollHeight;
}
