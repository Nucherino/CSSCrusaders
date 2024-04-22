const ws = true;
let socket = null;

function addText () {
  document.getElementById("post-text-box").focus();
  document.getElementById("post-title").innerHTML += "Posts";
}

function initWS(){
  console.log("HI THERE");
  socket = io("https://csscrusaders.com", {
    path: "/",
    transports: ["websocket", "polling"]
  });
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

  socket.on("like", (likeData) => {
    updateLikes(likeData);
    console.log("user liked message");
  });

  socket.on("connect_error", (err) => {
    // the reason of the error, for example "xhr poll error"
    console.log(err.message);
  
    // some additional description, for example the status code of the initial HTTP response
    console.log(err.description);
  
    // some additional context, for example the XMLHttpRequest object
    console.log(err.context);
  });
}

function updateLikes(likeData) {
  postID = likeData.postId;
  liked = likeData.liked;

  counter = document.getElementById(`${postID}_like_count`);
  counter.innerText = likeData.likeCount;
}

function likeClicked(postId){
  if(ws){
    console.log("like button clicked");
    socket.emit("like", {"postId": postId});
  } 
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
            <span id="${message.post_id}_like_button" class="material-icons" onclick='likeClicked(${message.post_id}); return false;'>thumb_up</span>
            <span id="${message.post_id}_like_count" class="like-count">${message.likeCount}</span>
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
            <span id="${message.post_id}_like_button" class="material-icons" onclick='likeClicked(${message.post_id}); return false;'>thumb_up</span>
            <span id="${message.post_id}_like_count" class="like-count">${message.likeCount}</span>
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