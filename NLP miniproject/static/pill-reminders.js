// Add the function in pill-reminders.js
function addPill() {
    // Retrieve form values
    const pillName = document.getElementById('pillName').value.trim();
    const dosage = document.getElementById('dosage').value.trim();
    const frequency = document.getElementById('frequency').value;
    const reminderTime = document.getElementById('reminderTime').value;
    const status = document.getElementById('status').value;

    // Validate required fields
    if (!pillName || !dosage || !reminderTime) {
        alert('Please fill out all required fields (Pill Name, Dosage, and Reminder Time).');
        return;
    }

    // Create timeline container if it doesn't exist
    const timelineContainer = document.getElementById('timelineContainer');
    if (!timelineContainer) {
        alert('Timeline container not found.');
        return;
    }

    // Create a new timeline item for the pill
    const timelineItem = document.createElement('div');
    timelineItem.className = 'timeline-item';

    // Convert status to capitalize the first letter (e.g., "taken" -> "Taken")
    const formattedStatus = status.charAt(0).toUpperCase() + status.slice(1);

    // Generate HTML for the timeline item
    timelineItem.innerHTML = `
        <div class="pill-time">${reminderTime}</div>
        <div>${pillName} (${dosage})</div>
        <div class="pill-frequency">Frequency: ${frequency}</div>
        <div class="status ${status.toLowerCase()}">${formattedStatus}</div>
    `;

    // Append the new item to the timeline container
    timelineContainer.appendChild(timelineItem);

    // Clear the form fields
    document.getElementById('pillForm').reset();
}

// Utility function to capitalize the first letter of a string (if needed)
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
