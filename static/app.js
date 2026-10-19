const tasksElement = document.querySelector("#tasks");
const messageElement = document.querySelector("#message");
const counterElement = document.querySelector("#counter");

const labels = { once: "חד-פעמית", daily: "יומית", weekly: "שבועית" };

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "הפעולה נכשלה");
  }
  return response.status === 204 ? null : response.json();
}

function escapeHtml(value) {
  const node = document.createElement("div");
  node.textContent = value;
  return node.innerHTML;
}

async function loadTasks() {
  try {
    const tasks = await request("/api/tasks");
    counterElement.textContent = `${tasks.filter((task) => task.status === "open").length} פתוחות`;
    tasksElement.innerHTML = tasks.length
      ? tasks.map((task) => `
          <article class="task ${task.status === "done" ? "done" : ""}">
            <button class="check" data-action="toggle" data-id="${task.id}" data-status="${task.status}" aria-label="שינוי סטטוס">${task.status === "done" ? "✓" : ""}</button>
            <div>
              <h3>${escapeHtml(task.title)}</h3>
              <p>${escapeHtml(task.assignee)} · ${labels[task.frequency]}${task.due_date ? ` · ${task.due_date}` : ""}</p>
            </div>
            <button class="delete" data-action="delete" data-id="${task.id}">מחיקה</button>
          </article>`).join("")
      : "<p class='empty'>אין עדיין משימות. זה זמן טוב להתחיל.</p>";
    messageElement.textContent = "";
  } catch (error) {
    messageElement.textContent = error.message;
  }
}

document.querySelector("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: document.querySelector("#title").value,
    assignee: document.querySelector("#assignee").value || "כולם",
    due_date: document.querySelector("#due-date").value || null,
    frequency: document.querySelector("#frequency").value,
  };
  try {
    await request("/api/tasks", { method: "POST", body: JSON.stringify(payload) });
    event.target.reset();
    document.querySelector("#assignee").value = "כולם";
    await loadTasks();
  } catch (error) {
    messageElement.textContent = error.message;
  }
});

tasksElement.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  try {
    if (button.dataset.action === "toggle") {
      const status = button.dataset.status === "done" ? "open" : "done";
      await request(`/api/tasks/${button.dataset.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
    } else {
      await request(`/api/tasks/${button.dataset.id}`, { method: "DELETE" });
    }
    await loadTasks();
  } catch (error) {
    messageElement.textContent = error.message;
  }
});

loadTasks();

