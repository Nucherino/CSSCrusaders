const ws = true;
let socket = null;

function addText () {
  document.getElementById("post-text-box").focus();
  document.getElementById("post-title").innerHTML += "Posts";
  if(ws){
    socket = new WebSocket('ws://' + window.location.host + "/websocket");
  }
}

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
    renderMessage(ws_message);
    const message = ws_message.content;
    console.log("Here is socket.on message: ");
    console.log(message);
  });
}
function sendChat () {
    const chatTextBox = document.getElementById('post-text-box');
    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws){
        console.log("Sending message over websocket");
        socket.emit("message", {"message": message});
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
  const postsContainer = document.getElementById("posts-container");
  postsContainer.innerHTML = "";
  messages.forEach(message => {
      const postElement = document.createElement("div");
      postElement.classList.add("list-posts");
      postElement.dataset.postId = message.post_id;
      postElement.dataset.username = message.username;
      postElement.innerHTML = `
          <img src="${message.image}" alt="Profile Picture" width="50" height="50">
          ${message.username}: ${message.content}
          <div class="post-likes">
            <span class="material-icons">thumb_up</span>
            <span class="like-count">${message.likeCount}</span>
          </div>
      `;
      postsContainer.appendChild(postElement);
      postsContainer.scrollTop = postsContainer.scrollHeight;
  });
}

function renderMessage(message) {
  const postsContainer = document.getElementById("posts-container");
  const postElement = document.createElement("div");
  postElement.classList.add("list-posts");
  postElement.dataset.postId = message.post_id;
  postElement.dataset.username = message.username;
  postElement.innerHTML = `
      <img src="${message.image}" alt="Profile Picture" width="50" height="50">
      ${message.username}: ${message.content}
      <div class="post-likes">
            <span class="material-icons">thumb_up</span>
            <span class="like-count">${message.likeCount}</span>
      </div>
  `;
  postsContainer.appendChild(postElement);
  postsContainer.scrollTop = postsContainer.scrollHeight;
}

function welcome(){
    addText();
    fetchMessages();
    if(ws){
        initWS();
    }
}

document.querySelectorAll(".post-likes").forEach(like => {
  like.addEventListener("click", function() {
    const postId = this.parentElement.dataset.postId;
    const counter = this.querySelector(".like-count");
    const isLiked = this.classList.contains("liked");
    const username = this.parentElement.dataset.username;
    fetch("/like", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ postId: postId, username: username })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then(data => {
      if (data.liked) {
        like.classList.add("liked");
      } else {
        like.classList.remove("liked");
      }
      counter.innerText = data.likeCount;
    })
    .catch(error => {
      console.error("Error:", error);
    });
  });
});