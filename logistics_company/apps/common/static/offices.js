// offices.js
import { getOffices, saveOffices, getCurrentUser } from "./storage.js";

let query = "";

/* ===== helpers ===== */
function qs(id) {
  return document.getElementById(id);
}

const modal = () => qs("officeModal");

function isAdmin() {
  const u = getCurrentUser();
  return u && u.role === "admin";
}

/* ===== modal helpers ===== */
function openModal(title) {
  qs("officeModalTitle").textContent = title;
  modal().classList.add("open");
  modal().setAttribute("aria-hidden", "false");
  setTimeout(() => qs("oName")?.focus(), 0);
}

function closeModal() {
  modal().classList.remove("open");
  modal().setAttribute("aria-hidden", "true");
  qs("officeForm")?.reset();
  qs("officeId").value = "";
}

function fillForm(o) {
  qs("officeId").value = o?.id ?? "";
  qs("oName").value = o?.name ?? "";
  qs("oCity").value = o?.city ?? "";
  qs("oAddress").value = o?.address ?? "";
  qs("oPhone").value = o?.phone ?? "";
}

/* ===== render ===== */
function render() {
  const tbody = qs("officesTableBody");
  if (!tbody) return;

  const offices = getOffices();
  const q = query.trim().toLowerCase();

  const visible = q
    ? offices.filter(o =>
        (o.name || "").toLowerCase().includes(q) ||
        (o.city || "").toLowerCase().includes(q) ||
        (o.address || "").toLowerCase().includes(q)
      )
    : offices;

  tbody.innerHTML = "";

  visible.forEach(o => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${o.name}</td>
      <td>${o.city}</td>
      <td>${o.address}</td>
      <td>${o.phone || ""}</td>
      <td>
        <button class="btn-icon" data-action="edit" data-id="${o.id}" title="Edit">✏️</button>
        <button class="btn-icon" data-action="delete" data-id="${o.id}" title="Delete">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const countEl = qs("officesCountInfo");
  if (countEl) {
    countEl.textContent = `Showing ${visible.length} results`;
  }

  // само admin може да управлява
  if (!isAdmin()) {
    const addBtn = qs("addOfficeBtn");
    if (addBtn) addBtn.style.display = "none";

    tbody.querySelectorAll("button[data-action]").forEach(b => {
      b.disabled = true;
      b.style.opacity = "0.35";
      b.style.cursor = "not-allowed";
      b.title = "Only admin can manage offices";
    });
  }
}

/* ===== actions ===== */
function openAdd() {
  if (!isAdmin()) return alert("Only admin can manage offices.");
  fillForm(null);
  openModal("Add Office");
}

function openEdit(id) {
  if (!isAdmin()) return alert("Only admin can manage offices.");
  const offices = getOffices();
  const office = offices.find(o => o.id === id);
  if (!office) return;
  fillForm(office);
  openModal("Edit Office");
}

function del(id) {
  if (!isAdmin()) return alert("Only admin can manage offices.");

  const offices = getOffices();
  const idx = offices.findIndex(o => o.id === id);
  if (idx === -1) return;

  const office = offices[idx];
  if (!confirm(`Delete office "${office.name}"?`)) return;

  offices.splice(idx, 1);
  saveOffices(offices);
  render();
}

/* ===== form submit ===== */
function onSave(e) {
  e.preventDefault();
  if (!isAdmin()) return alert("Only admin can manage offices.");

  const idRaw = qs("officeId").value;
  const name = qs("oName").value.trim();
  const city = qs("oCity").value.trim();
  const address = qs("oAddress").value.trim();
  const phone = qs("oPhone").value.trim();

  if (!name || !city || !address) {
    alert("Please fill Name, City and Address.");
    return;
  }

  const offices = getOffices();

  // EDIT
  if (idRaw) {
    const id = Number(idRaw);
    const idx = offices.findIndex(o => o.id === id);
    if (idx === -1) return;

    offices[idx] = { ...offices[idx], name, city, address, phone };
    saveOffices(offices);

    closeModal();
    render();
    return;
  }

  // CREATE
  offices.push({ id: Date.now(), name, city, address, phone });
  saveOffices(offices);

  closeModal();
  render();
}

/* ===== init ===== */
export default function initOfficesPage() {
  console.log("Offices JS loaded");

  const tbody = qs("officesTableBody");
  if (!tbody) return;

  // initial render
  render();

  qs("addOfficeBtn")?.addEventListener("click", openAdd);

  qs("officesSearch")?.addEventListener("input", e => {
    query = e.target.value || "";
    render();
  });

  tbody.addEventListener("click", e => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const id = Number(btn.dataset.id);
    const action = btn.dataset.action;

    if (action === "edit") openEdit(id);
    if (action === "delete") del(id);
  });

  qs("officeModalCloseBtn")?.addEventListener("click", closeModal);
  qs("officeCancelBtn")?.addEventListener("click", closeModal);

  modal()?.addEventListener("click", e => {
    if (e.target?.dataset?.close) closeModal();
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && modal()?.classList.contains("open")) {
      closeModal();
    }
  });

  qs("officeForm")?.addEventListener("submit", onSave);
}
