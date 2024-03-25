function addText () {
    document.getElementById("post-title").innerHTML += "Posts";
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