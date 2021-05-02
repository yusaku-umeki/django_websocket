(()=>{
  const roomName = window.location.pathname;
  const wsScheme = window.location.protocol == "https:" ? "wss" : "ws";

  const chatSocket = new WebSocket(
      wsScheme
      + "://"
      + window.location.host
      + '/ws'
      + roomName
  );

  chatSocket.addEventListener("message",(e)=>{
    const data = JSON.parse(e.data);
    if(data.error_msg){
      alert(data.error_msg);
    } else {
      const newChatItem = createChatItem(data);
      document.getElementById("chat-list").appendChild(newChatItem);
    }
  });

  chatSocket.addEventListener("close",(e)=>{
    console.error('Chat socket closed unexpectedly');
  });

  // ファイル選択時
  document.getElementById("chat-file-input").addEventListener("change", (e)=>{
    chatFile = e.target.files[0];
    if(chatFile.size > 10 * 1024 * 1024){
      alert("ファイルサイズは10MB以下である必要があります。圧縮するかクラウドサービスをご利用ください。");
    } else {
      chatSocket.send(
        JSON.stringify({
          file_name: chatFile.name,
        })
      );
      chatSocket.send(chatFile);
      e.target.value = "";
    }
  });

  // テキスト送信時
  document.getElementById('chat-message-submit').addEventListener("click", (e)=>{
    const messageInput = document.getElementById('chat-message-input');
    const message = messageInput.value;
    if (message && message.match(/\S/g)) {
      chatSocket.send(
        JSON.stringify({
          "message": message,
        })
      );
      messageInput.value = "";
    }
  });

})();

// WebSocketで受けたデータから新しいchatを生成する
function createChatItem(data) {
  const newChatItem = document.createElement("li");
  newChatItem.classList.add("chat-list__item");
  // 時間を先にappend
  newChatItem.appendChild(getTime(data));
  if (data.message) {
    // テキスト
    const content = document.createElement("span");
    const newMessage = document.createTextNode(data.message);
    content.classList.add("chat-list__content");
    content.appendChild(newMessage);
    newChatItem.appendChild(content)
  } else {
    // ファイル
    const url = data.file_url;
    const file_name = data.file_name;
    const newImg = document.createElement("img");
    newImg.setAttribute("src", url);
    newImg.setAttribute("alt", file_name);
    newImg.setAttribute("class", "chat-list__src");
    newChatItem.appendChild(newImg);
  }
  return newChatItem;
}

function getTime(data) {
  const time = document.createElement("span");
  time.classList.add("chat-list__time");
  newTime = document.createTextNode(data.time);
  time.appendChild(newTime);
  return time;
}
