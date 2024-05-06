const ws = true;
let socket = null;

function addText () {
  document.getElementById("post-text-box").focus();
  document.getElementById("post-title").innerHTML += "Posts";
}

function initWS(){
  console.log("HI THERE");

  //* comment this out on deployment 
  socket = io("https://csscrusaders.com", {
    //path: "/",
    transports: ["websocket"]
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

  socket.on("counter", (ws_counter) => {
    const secondsLeft = ws_counter.counter;
    const message = ws_counter.message;

    const element = document.getElementById(`${message.post_id}_delayed_post`);

    if(element === null) {
      const main = document.getElementById("pending-message-container");

      const postElement = document.createElement("div");
      postElement.id = `${message.post_id}_delayed_post`;
      postElement.dataset.postId = message.post_id;
      postElement.innerHTML = `${message.username}: ${message.content}`;

      const postTimer = document.createElement("p");
      postTimer.id = `${message.post_id}_timer`;

      postElement.appendChild(postTimer);
      main.appendChild(postElement);
    } 

    updateCounter(ws_counter.message, secondsLeft);
  })

  socket.on("connect_error", (err) => {
    // the reason of the error, for example "xhr poll error"
    console.log(err.message);
  
    // some additional description, for example the status code of the initial HTTP response
    console.log(err.description);
  
    // some additional context, for example the XMLHttpRequest object
    console.log(err.context);
  });
}

function updateCounter(message, secondsLeft){
  const messageID = message.post_id;
  const element = document.getElementById(`${messageID}_delayed_post`);
  const timer = document.getElementById(`${messageID}_timer`);
  if (secondsLeft === 1) { 
    timer.innerText = `Sends in ${String(secondsLeft)} second`;
    setTimeout(function(){ element.remove() }, 1000);
  } else {
    timer.innerText = `Sends in ${String(secondsLeft)} seconds`;
  }
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

    const delayBox = document.getElementById('post-delay-box');
    let delay = Number(delayBox.value);

    if(delay === NaN){
      delay = 0;
    }
    delayBox.value = "";

    if (ws){
        console.log("Sending message over websocket");
        socket.emit("message", {"message": message, 'delay':delay});
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
          <a href='/profile/${message.username}'>${message.username}</a>: ${message.content}
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
      <a href='/profile/${message.username}'>${message.username}</a>: ${message.content}
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
