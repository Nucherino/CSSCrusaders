const ws = false;
let socket = null;

function addText () {
  document.getElementById("post-text-box").focus();
  document.getElementById("post-title").innerHTML += "Posts";
  if(ws){
    socket = new WebSocket('ws://' + window.location.host + "/websocket");
  }  
}

// Function to fetch messages from the server
function fetchInitialLikeCountsAndMessages() {
    fetch("/get-messages")
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch messages");
        }
        return response.json();
    })
    .then(messages => {
        // Once messages are received, render them in the HTML container
        renderMessages(messages);
        // Fetch initial like counts for each message
        fetchInitialLikeCounts(messages);
    })
    .catch(error => {
        console.error("Error fetching messages:", error);
    });
}

// Function to render messages in the HTML container
function renderMessages(messages) {
    const messagesContainer = document.getElementById("messages-container");

    // Clear previous messages
    messagesContainer.innerHTML = "";

    // Iterate over each message and create HTML elements to display them
    messages.forEach(message => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.textContent = message.content; // Adjust accordingly based on your message structure
        messagesContainer.appendChild(messageElement);
    });
}

function fetchInitialLikeCounts(messages) {
    messages.forEach(message => {
        const postId = message.post_id; // Assuming message object has a 'post_id' property
        const likeContainer = document.querySelector(`.post-likes[data-post-id="${postId}"]`);
        fetch(`/like?postId=${postId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                const counter = likeContainer.querySelector(".like-count");
                counter.innerText = data.likeCount;
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });
}
document.addEventListener("DOMContentLoaded", fetchInitialLikeCountsAndMessages);
function handleLikeButtonClick() {
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
}