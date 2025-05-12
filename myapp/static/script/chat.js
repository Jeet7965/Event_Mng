document.getElementById('chat-form').addEventListener('submit', async function (e) {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const message = input.value;
  if (!message.trim()) return;

  const chatBox = document.getElementById('chat-messages');
  chatBox.innerHTML += `<div class="text-right"><strong>You:</strong> ${message}</div>`;

  input.value = '';

  const response = await fetch("{% url 'chatbot-response' %}", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}',
    },
    body: JSON.stringify({ message })
  });
  const data = await response.json();
  console.log("Bot response:", data); // 👈 Add this to debug

  if (data.response) {
    chatBox.innerHTML += `<div><strong>Bot:</strong> ${data.response}</div>`;
  } else {
    chatBox.innerHTML += `<div><strong>Bot:</strong> Sorry, an error occurred.</div>`;
  }

});