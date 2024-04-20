const ws = true;
let socket = null;

function initWS(){
  console.log("HI THERE");
  socket = io();
  console.log(socket);

  socket.on("connect", () => {
    console.log("user connected!");
  })

  socket.on("disconnect", () => {
    console.log("user disconnected");
  })

  socket.on("message", (ws_message) => {
    const message = JSON.parse(ws_message.data);
    console.log("Here is socket.on message: ");
    console.log(message);
    console.log(ws_message);
    const messageType = message.messageType;
    if(messageType === 'message'){
      console.log("message sent");
    }
  });
}
function sendChat () {
    const chatTextBox = document.getElementById('post-text-box');
    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws){
        console.log("Sending message over websocket");
        socket.send(JSON.stringify({"message": message}));
    }
    else {
        console.log("Fetching chat messages using get request");
        fetch("/chat-messages", {
            method: "POST",
            body: JSON.stringify({"message":message}),
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then((result) => {
            console.log(result);
        })
    }
  chatTextBox.focus();
}

function fetchMessages() {
    fetch("/get-messages")
        .then(response => {
            return response.json();
        })
        .then(messages => {
            renderMessages(messages);
        })
        .catch(error => {
            console.error("Error fetching messages:", error);
        });
}
    // Function to render messages in the HTML container
function renderMessages(messages) {
    const messagesContainer = document.getElementById("messages-container");
    messagesContainer.innerHTML = "";
    messages.forEach(message => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.textContent = message.content;
        messagesContainer.appendChild(messageElement);
    });
}
function renderMessage(message) {
        const messageContainer = document.getElementById("posts-container");
        messageContainer.innerHTML = "";
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.textContent = message.content;
        messageContainer.appendChild(messageElement);
}

function welcome(){
  fetchMessages();
  if(ws){
    initWS();
  }
}