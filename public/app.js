function addText () {
    document.getElementById("post-title").innerHTML += "Posts";
}
document.querySelectorAll(".post-likes").forEach(like => {
  like.addEventListener("click", function() {
    const postId = this.dataset.postId;
    const counter = this.querySelector(".like-count");
    const isLiked = this.classList.contains("liked");

    fetch("/like", {
      method: isLiked ? "DELETE" : "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ postId: postId })
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
  });
});