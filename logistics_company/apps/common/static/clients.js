// clients.js
import {
  getClients,
  saveClients,
  getCurrentUser,
  getUsers,
  saveUsers
} from "./storage.js";

let query = "";

function qs(id) {
  return document.getElementById(id);
}

const modal = () => qs("clientModal");

function isAdmin() {
  const u = getCurrentUser();
  return u && u.role === "admin";
}

function upsertClientAsUser({ name, email, password }) {
  const users = getUsers();
  const idx = users.findIndex(u => u.email === email);
  const existing = idx >= 0 ? users[idx] : null;

  const userObj = {
    id: existing?.id ?? Date.now(),
    name: name || existing?.name || "",
    email,
    password:
      password && password.trim()
        ? password.trim()
        : existing?.password || "client123",
    role: "client"
  };

  if (idx >= 0) {
    users[idx] = userObj;
  } else {
    users.push(userObj);
  }

  saveUsers(users);
}

function removeClientUser(email) {
  const users = getUsers();
  saveUsers(users.filter(u => u.email !== email));
}

function openModal(title) {
  qs("clientModalTitle").textContent = title;
  modal().classList.add("open");
  modal().setAttribute("aria-hidden", "false");
  setTimeout(() => qs("cName")?.focus(), 0);
}

function closeModal() {
  modal().classList.remove("open");
  modal().setAttribute("aria-hidden", "true");
  qs("clientForm")?.reset();
  qs("clientId").value = "";
  qs("cPassword").value = "";
}

function fillForm(c) {
  qs("clientId").value = c?.id ?? "";
  qs("cName").value = c?.name ?? "";
  qs("cEmail").value = c?.email ?? "";
  qs("cPhone").value = c?.phone ?? "";
  qs("cPassword").value = "";
}

function render() {
  const tbody = qs("clientsTableBody");
  if (!tbody) return;

  const clients = getClients();
  const q = query.trim().toLowerCase();

  const visible = q
    ? clients.filter(c =>
        (c.name || "").toLowerCase().includes(q) ||
        (c.email || "").toLowerCase().includes(q) ||
        (c.phone || "").toLowerCase().includes(q)
      )
    : clients;

  tbody.innerHTML = "";

  visible.forEach(c => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.name}</td>
      <td>${c.email}</td>
      <td>${c.phone}</td>
      <td>
        <button class="btn-icon" data-action="edit" data-id="${c.id}" title="Edit">✏️</button>
        <button class="btn-icon" data-action="delete" data-id="${c.id}" title="Delete">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  qs("clientsCountInfo").textContent = `Showing ${visible.length} results`;

  if (!isAdmin()) {
    qs("addClientBtn").style.display = "none";
    tbody.querySelectorAll("button").forEach(b => {
      b.disabled = true;
      b.style.opacity = "0.35";
      b.style.cursor = "not-allowed";
      b.title = "Only admin can manage clients";
    });
  }
}

function openAdd() {
  if (!isAdmin()) return alert("Only admin can manage clients.");
  fillForm(null);
  openModal("Add Client");
}

function openEdit(id) {
  if (!isAdmin()) return alert("Only admin can manage clients.");
  const clients = getClients();
  const c = clients.find(x => x.id === id);
  if (!c) return;
  fillForm(c);
  openModal("Edit Client");
}

function deleteClient(id) {
  if (!isAdmin()) return alert("Only admin can manage clients.");
  if (!confirm("Delete this client?")) return;

  const clients = getClients();
  const c = clients.find(x => x.id === id);
  if (c) {
    removeClientUser(c.email);
  }
  saveClients(clients.filter(x => x.id !== id));
  render();
}

function saveClient(e) {
  e.preventDefault();
  if (!isAdmin()) return alert("Only admin can manage clients.");

  const id = qs("clientId").value;
  const name = qs("cName").value.trim();
  const email = qs("cEmail").value.trim();
  const phone = qs("cPhone").value.trim();
  const password = qs("cPassword").value;

  if (!name || !email) {
    return alert("Name and Email are required.");
  }

  const clients = getClients();
  const existingIdx = clients.findIndex(c => c.id === (id ? Number(id) : -1));

  if (existingIdx >= 0) {
    clients[existingIdx] = { ...clients[existingIdx], name, email, phone };
  } else {
    clients.push({ id: Date.now(), name, email, phone });
  }

  saveClients(clients);
  upsertClientAsUser({ name, email, password });

  closeModal();
  render();
}

function init() {
  const searchInput = qs("clientsSearch");
  if (searchInput) {
    searchInput.addEventListener("input", e => {
      query = e.target.value;
      render();
    });
  }

  const addBtn = qs("addClientBtn");
  if (addBtn) {
    addBtn.addEventListener("click", openAdd);
  }

  const tbody = qs("clientsTableBody");
  if (tbody) {
    tbody.addEventListener("click", e => {
      const btn = e.target.closest("button[data-action]");
      if (!btn) return;
      const action = btn.dataset.action;
      const id = Number(btn.dataset.id);
      if (action === "edit") openEdit(id);
      if (action === "delete") deleteClient(id);
    });
  }

  const form = qs("clientForm");
  if (form) {
    form.addEventListener("submit", saveClient);
  }

  const closeBtn = modal()?.querySelector(".modal-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", closeModal);
  }

  modal()?.addEventListener("click", e => {
    if (e.target === modal()) closeModal();
  });

  render();
}

document.addEventListener("DOMContentLoaded", init);
