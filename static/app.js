const tasksElement = document.querySelector("#tasks");
const messageElement = document.querySelector("#message");
const counterElement = document.querySelector("#counter");
const formElement = document.querySelector("#task-form");
const formTitleElement = document.querySelector("#form-title");
const submitButtonElement = document.querySelector("#submit-button");
const cancelEditElement = document.querySelector("#cancel-edit");

const labels = { once: "חד-פעמית", daily: "יומית", weekly: "שבועית" };

let currentTasks = [];
let editingTaskId = null;

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
    currentTasks = tasks;

    counterElement.textContent =
      `${tasks.filter((task) => task.status === "open").length} פתוחות`;

    tasksElement.innerHTML = tasks.length
      ? tasks
          .map(
            (task) => `
              <article class="task ${task.status === "done" ? "done" : ""}">
                <button
                  class="check"
                  data-action="toggle"
                  data-id="${task.id}"
                  data-status="${task.status}"
                  aria-label="שינוי סטטוס"
                >
                  ${task.status === "done" ? "✓" : ""}
                </button>

                <div>
                  <h3>${escapeHtml(task.title)}</h3>
                  <p>
                    ${escapeHtml(task.assignee)}
                    · ${labels[task.frequency]}
                    ${task.due_date ? ` · ${task.due_date}` : ""}
                  </p>
                </div>

                <button
                  class="edit"
                  data-action="edit"
                  data-id="${task.id}"
                >
                  עריכה
                </button>

                <button
                  class="delete"
                  data-action="delete"
                  data-id="${task.id}"
                >
                  מחיקה
                </button>
              </article>
            `,
          )
          .join("")
      : "<p class='empty'>אין עדיין משימות. זה זמן טוב להתחיל.</p>";

    messageElement.textContent = "";
  } catch (error) {
    messageElement.textContent = error.message;
  }
}

function resetForm() {
  editingTaskId = null;
  formElement.reset();
  document.querySelector("#assignee").value = "כולם";
  formTitleElement.textContent = "משימה חדשה";
  submitButtonElement.textContent = "הוספת משימה";
  cancelEditElement.hidden = true;
}

function startEditing(task) {
  editingTaskId = task.id;
  document.querySelector("#title").value = task.title;
  document.querySelector("#assignee").value = task.assignee;
  document.querySelector("#due-date").value = task.due_date || "";
  document.querySelector("#frequency").value = task.frequency;
  formTitleElement.textContent = "עריכת משימה";
  submitButtonElement.textContent = "שמירת שינויים";
  cancelEditElement.hidden = false;
  formElement.scrollIntoView({ behavior: "smooth", block: "center" });
  document.querySelector("#title").focus();
}

async function updateTask(id, changes) {
  await request(`/api/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });

  await loadTasks();
}

async function deleteTask(id) {
  await request(`/api/tasks/${id}`, {
    method: "DELETE",
  });

  await loadTasks();
}

formElement.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: document.querySelector("#title").value,
    assignee: document.querySelector("#assignee").value || "כולם",
    due_date: document.querySelector("#due-date").value || null,
    frequency: document.querySelector("#frequency").value,
  };
  try {
    if (editingTaskId === null) {
      await request("/api/tasks", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      await loadTasks();
    } else {
      await updateTask(editingTaskId, payload);
    }
    resetForm();
  } catch (error) {
    messageElement.textContent = error.message;
  }
});

cancelEditElement.addEventListener("click", resetForm);

tasksElement.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");

  if (!button) {
    return;
  }

  const action = button.dataset.action;
  const id = button.dataset.id;

  try {
    if (action === "toggle") {
      const status =
        button.dataset.status === "done" ? "open" : "done";

      await updateTask(id, { status });
    }

    if (action === "delete") {
      await deleteTask(id);
      if (Number(id) === editingTaskId) {
        resetForm();
      }
    }

    if (action === "edit") {
      const task = currentTasks.find((item) => item.id === Number(id));
      if (task) {
        startEditing(task);
      }
    }
  } catch (error) {
    messageElement.textContent = error.message;
  }
});

loadTasks();

