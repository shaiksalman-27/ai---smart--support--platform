async function loadAdminTickets() {
  try {
    const response = await fetch("/tickets");
    const tickets = await response.json();

    const container = document.getElementById("ticketsContainer");
    container.innerHTML = "";

    if (tickets.length === 0) {
      container.innerHTML = "<p>No tickets found.</p>";
      return;
    }

    tickets.forEach(ticket => {
      const card = document.createElement("div");
      card.className = "card";

      const historyHtml = ticket.history
        .map(item => `<li>${item}</li>`)
        .join("");

      card.innerHTML = `
        <h2>Ticket #${ticket.ticket_id}</h2>
        <p><strong>Issue:</strong> ${ticket.issue}</p>
        <p><strong>Category:</strong> ${ticket.category}</p>
        <p><strong>Priority:</strong> <span class="badge ${ticket.priority.toLowerCase()}">${ticket.priority}</span></p>
        <p><strong>Escalation:</strong> ${ticket.escalation ? "Yes" : "No"}</p>
        <p><strong>Status:</strong> ${ticket.status}</p>
        <p><strong>Created At:</strong> ${ticket.created_at}</p>
        <p><strong>Solution:</strong> ${ticket.solution}</p>

        <label><strong>Update Status:</strong></label>
        <select id="status-${ticket.ticket_id}">
          <option value="Open">Open</option>
          <option value="In Progress">In Progress</option>
          <option value="Closed">Closed</option>
        </select>
        <button onclick="updateStatus(${ticket.ticket_id})">Update</button>

        <h3>History</h3>
        <ul>${historyHtml}</ul>
      `;

      container.appendChild(card);

      setTimeout(() => {
        const select = document.getElementById(`status-${ticket.ticket_id}`);
        if (select) {
          select.value = ticket.status;
        }
      }, 0);
    });

  } catch (error) {
    console.error(error);
    alert("Error loading tickets.");
  }
}

async function updateStatus(ticketId) {
  const select = document.getElementById(`status-${ticketId}`);
  const status = select.value;

  try {
    const response = await fetch(`/tickets/${ticketId}/status`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ status: status })
    });

    const data = await response.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    alert("Status updated successfully");
    loadAdminTickets();

  } catch (error) {
    console.error(error);
    alert("Error updating status");
  }
}

window.onload = loadAdminTickets;