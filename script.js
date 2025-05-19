// Load missing people
async function loadMissingPeople() {
  const res = await fetch('/api/get_missing_people');
  const people = await res.json();
  const grid = document.getElementById('people-grid');
  grid.innerHTML = '';
  people.forEach(p => {
    grid.innerHTML += `
      <div class="person-card">
        <strong>${p.name}</strong><br/>
        Missing since: ${p.date_missing}<br/>
        Location: ${p.location}<br/>
        Confidence: ${p.confidence_percentage}%<br/>
      </div>`;
  });
}

// Submit form
document.getElementById('missing-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = {
    name: document.getElementById('name').value,
    date_missing: document.getElementById('date_missing').value,
    location: document.getElementById('location').value,
    zip_code: document.getElementById('zip_or_coord').value,
    confidence_percentage: 95
  };
  await fetch('/api/report_missing_person', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  alert("Person reported successfully!");
  loadMissingPeople();
});

// Generate chart
async function generateChart() {
  const res = await fetch('/api/generate_chart');
  const chart = await res.json();
  document.getElementById('location-chart').src = chart.chart;
}

// Send message to chatbot and get reply
async function sendMessage() {
  const input = document.getElementById('chat-input');
  const chatBox = document.getElementById('chat-box');
  const userMessage = input.value.trim();

  if (!userMessage) return;

  // Show user message
  chatBox.innerHTML += `<div><strong>You:</strong> ${userMessage}</div>`;
  input.value = '';

  // Scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;

  // Show typing...
  chatBox.innerHTML += `<div><strong>AI:</strong> <span id="typing">Typing...</span></div>`;
  chatBox.scrollTop = chatBox.scrollHeight;

  // Get AI response
  setTimeout(async () => {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage })
    });

    const data = await res.json();
    document.getElementById('typing').innerText = data.reply;
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 500);
}

// Allow pressing Enter to send message
document.getElementById('chat-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    sendMessage();
  }
});

// On load
window.onload = () => {
  loadMissingPeople();
  generateChart();
};