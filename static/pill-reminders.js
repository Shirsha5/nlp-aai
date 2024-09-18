function addPill() {
  const pillName = document.getElementById('pillName').value;
  const dosage = document.getElementById('dosage').value;
  const frequency = document.getElementById('frequency').value;
  const reminderTime = document.getElementById('reminderTime').value;
  const status = document.getElementById('status').value;

  if (pillName && dosage && reminderTime) {
      const timelineContainer = document.getElementById('timelineContainer');

      const timelineItem = document.createElement('div');
      timelineItem.className = 'timeline-item';

      timelineItem.innerHTML = `
          <div class="pill-time">${reminderTime}</div>
          <div>${pillName} (${dosage})</div>
          <div class="status ${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</div>
      `;

      timelineContainer.appendChild(timelineItem);

      // Clear the form fields
      document.getElementById('pillForm').reset();
  } else {
      alert('Please fill out all required fields.');
  }
}



