// employees.js
import {
  getEmployees,
  saveEmployees,
  getCurrentUser,
  getUsers,
  saveUsers
} from "./storage.js";

let query = "";

function qs(id) {
  return document.getElementById(id);
}

function isAdmin() {
  const u = getCurrentUser();
  return u && u.role === "admin";
}

function upsertEmployeeAsUser({ name, email, password }) {
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
        : existing?.password || "emp123",
    role: "employee"
  };

  if (idx >= 0) {
    users[idx] = userObj;
  } else {
    users.push(userObj);
  }

  saveUsers(users);
}

function removeEmployeeUser(email) {
  const users = getUsers();
  saveUsers(users.filter(u => u.email !== email));
}

const modal = () => qs("employeeModal");

function openModal() {
  modal().classList.add("open");
  modal().setAttribute("aria-hidden", "false");
  setTimeout(() => qs("empName")?.focus(), 0);
}

function closeModal() {
  modal().classList.remove("open");
  modal().setAttribute("aria-hidden", "true");
  qs("employeeForm")?.reset();
  qs("employeeId").value = "";
  qs("empPassword").value = "";
}

function setModalTitle(text) {
  qs("employeeModalTitle").textContent = text;
}

function fillForm(emp) {
  qs("employeeId").value = emp?.id ?? "";
  qs("empName").value = emp?.name ?? "";
  qs("empEmail").value = emp?.email ?? "";
  qs("empRole").value = emp?.role ?? "Courier";
  qs("empOffice").value = emp?.office ?? "Downtown Office";
  qs("empPhone").value = emp?.phone ?? "";
  qs("empPassword").value = "";
}

function renderEmployeesTable() {
  const tbody = qs("employeesTableBody");
  if (!tbody) return;

  const employees = getEmployees();
  const q = query.trim().toLowerCase();

  const visible = q
    ? employees.filter(e =>
        (e.name || "").toLowerCase().includes(q) ||
        (e.email || "").toLowerCase().includes(q)
      )
    : employees;

  tbody.innerHTML = "";

  visible.forEach(emp => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${emp.name}</td>
      <td>${emp.email}</td>
      <td><span class="badge badge-info">${emp.role}</span></td>
      <td>${emp.office}</td>
      <td>${emp.phone}</td>
      <td>
        <button class="btn-icon" data-action="view" data-id="${emp.id}" title="View">👁️</button>
        <button class="btn-icon" data-action="edit" data-id="${emp.id}" title="Edit">✏️</button>
        <button class="btn-icon" data-action="delete" data-id="${emp.id}" title="Delete">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const count = qs("employeesCountInfo");
  if (count) {
    count.textContent = `Showing ${visible.length} results`;
  }

  if (!isAdmin()) {
    tbody
      .querySelectorAll(
        "button[data-action='edit'], button[data-action='delete']"
      )
      .forEach(b => {
        b.disabled = true;
        b.style.opacity = "0.35";
        b.style.cursor = "not-allowed";
        b.title = "Only admin can edit/delete employees";
      });

    const addBtn = qs("addEmployeeBtn");
    if (addBtn) addBtn.style.display = "none";
  }
}

function getEmployeeById(id) {
  return getEmployees().find(e => e.id === id);
}

function viewEmployee(id) {
  const emp = getEmployeeById(id);
  if (!emp) return;

  alert(
    `Employee:\n` +
      `Name: ${emp.name}\n` +
      `Email: ${emp.email}\n` +
      `Position: ${emp.role}\n` +
      `Office: ${emp.office}\n` +
      `Phone: ${emp.phone}`
  );
}

function onAddEmployee() {
  if (!isAdmin()) return alert("Only admin can manage employees.");
  setModalTitle("Add Employee");
  fillForm(null);
  openModal();
}

function onEditEmployee(id) {
  if (!isAdmin()) return alert("Only admin can manage employees.");
  const emp = getEmployeeById(id);
  if (!emp) return;
  setModalTitle("Edit Employee");
  fillForm(emp);
  openModal();
}

function onDeleteEmployee(id) {
  if (!isAdmin()) return alert("Only admin can manage employees.");

  const employees = getEmployees();
  const idx = employees.findIndex(e => e.id === id);
  if (idx === -1) return;

  const emp = employees[idx];
  if (!confirm(`Delete employee "${emp.name}"?`)) return;

  employees.splice(idx, 1);
  saveEmployees(employees);
  removeEmployeeUser(emp.email);

  renderEmployeesTable();
}

function onSaveEmployee(e) {
  e.preventDefault();
  if (!isAdmin()) return alert("Only admin can manage employees.");

  const idRaw = qs("employeeId").value;
  const name = qs("empName").value.trim();
  const email = qs("empEmail").value.trim();
  const role = qs("empRole").value;
  const office = qs("empOffice").value.trim();
  const phone = qs("empPhone").value.trim();
  const password = qs("empPassword").value;

  if (!name || !email || !role || !office) {
    alert("Please fill Name, Email, Position and Office.");
    return;
  }

  const employees = getEmployees();

  if (idRaw) {
    const id = Number(idRaw);
    const idx = employees.findIndex(x => x.id === id);
    if (idx === -1) return;

    const oldEmail = employees[idx].email;

    employees[idx] = { ...employees[idx], name, email, role, office, phone };
    saveEmployees(employees);

    if (oldEmail !== email) {
      removeEmployeeUser(oldEmail);
    }
    upsertEmployeeAsUser({ name, email, password });

    closeModal();
    renderEmployeesTable();
    return;
  }

  const newEmp = {
    id: Date.now(),
    name,
    email,
    role,
    office,
    phone
  };

  employees.push(newEmp);
  saveEmployees(employees);

  upsertEmployeeAsUser({ name, email, password });

  closeModal();
  renderEmployeesTable();
}

export default function initEmployeesPage() {
  console.log("Employees JS loaded");

  const addBtn = qs("addEmployeeBtn");
  const tbody = qs("employeesTableBody");
  const search = qs("employeesSearch");

  if (!addBtn || !tbody) return;

  addBtn.addEventListener("click", onAddEmployee);

  if (search) {
    search.addEventListener("input", e => {
      query = e.target.value || "";
      renderEmployeesTable();
    });
  }

  tbody.addEventListener("click", e => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const id = Number(btn.dataset.id);
    const action = btn.dataset.action;

    if (action === "view") viewEmployee(id);
    if (action === "edit") onEditEmployee(id);
    if (action === "delete") onDeleteEmployee(id);
  });

  qs("employeeModalCloseBtn")?.addEventListener("click", closeModal);
  qs("employeeCancelBtn")?.addEventListener("click", closeModal);

  modal()?.addEventListener("click", e => {
    if (e.target?.dataset?.close) closeModal();
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && modal()?.classList.contains("open")) {
      closeModal();
    }
  });

  qs("employeeForm")?.addEventListener("submit", onSaveEmployee);

  renderEmployeesTable();
}
