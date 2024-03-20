function sendPost() {
    const postBox = document.getElementById("chat-text-box");
    const message = postBox.value;
    postBox.value = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("POST", "/posts");
    request.send(JSON.stringify(messageJSON));
    postBox.focus();
}