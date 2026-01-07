// reports.js
import {
  getCurrentUser,
  getEmployees,
  getClients,
  getParcels
} from "./storage.js";

/* ===== helpers ===== */
function qs(id) {
  return document.getElementById(id);
}

const modal = () => qs("reportModal");

function role() {
  return getCurrentUser()?.role || null;
}

/* ===== modal helpers ===== */
function openModal(title, subtitle, bodyHtml) {
  qs("reportModalTitle").textContent = title;
  qs("reportModalSubtitle").textContent = subtitle;
  qs("reportModalBody").innerHTML = bodyHtml;

  modal().classList.add("open");
  modal().setAttribute("aria-hidden", "false");

  setTimeout(
    () => qs("reportModalBody")?.querySelector("select,input")?.focus(),
    0
  );
}

function closeModal() {
  modal().classList.remove("open");
  modal().setAttribute("aria-hidden", "true");
  qs("reportModalBody").innerHTML = "";
  qs("reportModalForm").dataset.mode = "";
}

/* ===== output ===== */
function setOutput(title, subtitle, summary, columns, rows) {
  qs("reportTitle").textContent = title;
  qs("reportSubtitle").textContent = subtitle;
  qs("reportSummary").textContent = summary || "";

  qs("reportThead").innerHTML = `
    <tr>${columns.map(c => `<th>${c}</th>`).join("")}</tr>
  `;

  qs("reportTbody").innerHTML = rows.length
    ? rows
        .map(r => `<tr>${r.map(v => `<td>${v ?? ""}</td>`).join("")}</tr>`)
        .join("")
    : `<tr>
         <td colspan="${columns.length}" style="color: var(--text-muted);">
           No results
         </td>
       </tr>`;
}

/* ===== utils ===== */
function fmtDate(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return String(iso);
  }
}

function getParcelCreatedAt(p) {
  return (
    p.createdAt ||
    (p.history && p.history[0] && p.history[0].date) ||
    null
  );
}

function getRegisteredBy(p) {
  return (
    p.registeredByEmail ||
    p.registeredBy ||
    p.createdByEmail ||
    p.createdBy ||
    (p.history && p.history[0] && p.history[0].by) ||
    null
  );
}

function getReceivedByClientMatch(p, client) {
  if (p.recipientEmail) return p.recipientEmail === client.email;

  const rec = String(p.recipient || "").toLowerCase();
  const name = String(client.name || "").toLowerCase();
  const email = String(client.email || "").toLowerCase();

  return (name && rec.includes(name)) || (email && rec.includes(email));
}

/* ===== filters ===== */
function populateFilterSelects() {
  const empSel = qs("filterEmployee");
  const clientSel = qs("filterClient");
  if (!empSel || !clientSel) return;

  empSel.innerHTML =
    `<option value="">Select employee</option>` +
    getEmployees()
      .map(e => `<option value="${e.email}">${e.name} (${e.email})</option>`)
      .join("");

  clientSel.innerHTML =
    `<option value="">Select client</option>` +
    getClients()
      .map(c => `<option value="${c.email}">${c.name} (${c.email})</option>`)
      .join("");
}

function requireAdminOrEmployee() {
  if (role() !== "admin" && role() !== "employee") {
    alert("Only admin/employee can generate company reports.");
    return false;
  }
  return true;
}

/* ===== reports ===== */
function reportAllEmployees() {
  if (!requireAdminOrEmployee()) return;

  const employees = getEmployees();
  setOutput(
    "All Employees",
    "Complete list of employees",
    `Total: ${employees.length}`,
    ["Name", "Email", "Position", "Office", "Phone"],
    employees.map(e => [e.name, e.email, e.role, e.office, e.phone])
  );
}

function reportAllClients() {
  if (!requireAdminOrEmployee()) return;

  const clients = getClients();
  setOutput(
    "All Clients",
    "Complete list of clients",
    `Total: ${clients.length}`,
    ["Name", "Email", "Phone"],
    clients.map(c => [c.name, c.email, c.phone])
  );
}

function reportAllParcels() {
  if (!requireAdminOrEmployee()) return;

  const parcels = getParcels();
  setOutput(
    "All Parcels",
    "All parcels in the system",
    `Total: ${parcels.length}`,
    ["Tracking", "Sender", "Recipient", "Status", "Price", "Created"],
    parcels.map(p => [
      p.tracking,
      p.sender,
      p.recipient,
      p.status,
      `$${Number(p.price).toFixed(2)}`,
      fmtDate(getParcelCreatedAt(p))
    ])
  );
}

function reportPendingDeliveries() {
  if (!requireAdminOrEmployee()) return;

  const parcels = getParcels().filter(p => p.status !== "Delivered");
  setOutput(
    "Pending Deliveries",
    "Parcels not delivered yet",
    `Total: ${parcels.length}`,
    ["Tracking", "Sender", "Recipient", "Status", "Price"],
    parcels.map(p => [
      p.tracking,
      p.sender,
      p.recipient,
      p.status,
      `$${Number(p.price).toFixed(2)}`
    ])
  );
}

/* ===== interactive reports ===== */
function askEmployeeThenReport() {
  if (!requireAdminOrEmployee()) return;

  const employees = getEmployees();

  openModal(
    "Parcels by Employee",
    "Choose an employee",
    `
      <div class="form-group">
        <label class="form-label">Employee</label>
        <select id="modalEmployeeSelect" class="select" required>
          <option value="">Select employee</option>
          ${employees
            .map(e => `<option value="${e.email}">${e.name} (${e.email})</option>`)
            .join("")}
        </select>
      </div>
    `
  );

  qs("reportModalForm").dataset.mode = "parcels_by_employee";
}

function runParcelsByEmployee(email) {
  const parcels = getParcels().filter(p => getRegisteredBy(p) === email);

  setOutput(
    "Parcels by Employee",
    `Employee: ${email}`,
    `Total parcels: ${parcels.length}`,
    ["Tracking", "Sender", "Recipient", "Status", "Price", "Created"],
    parcels.map(p => [
      p.tracking,
      p.sender,
      p.recipient,
      p.status,
      `$${Number(p.price).toFixed(2)}`,
      fmtDate(getParcelCreatedAt(p))
    ])
  );
}

function askIncomePeriod() {
  if (!requireAdminOrEmployee()) return;

  openModal(
    "Income Report",
    "Choose a time period",
    `
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">From</label>
          <input id="modalFrom" type="date" class="form-control" required />
        </div>
        <div class="form-group">
          <label class="form-label">To</label>
          <input id="modalTo" type="date" class="form-control" required />
        </div>
      </div>
    `
  );

  qs("reportModalForm").dataset.mode = "income_period";
}

function runIncomePeriod(fromStr, toStr) {
  const from = new Date(fromStr);
  const to = new Date(toStr);
  to.setHours(23, 59, 59, 999);

  const parcels = getParcels().filter(p => {
    const d = getParcelCreatedAt(p);
    if (!d) return false;
    const t = new Date(d).getTime();
    return t >= from.getTime() && t <= to.getTime();
  });

  const income = parcels.reduce((s, p) => s + Number(p.price || 0), 0);

  setOutput(
    "Income Report",
    `Period: ${fromStr} → ${toStr}`,
    `Parcels: ${parcels.length} | Total income: $${income.toFixed(2)}`,
    ["Tracking", "Price", "Created", "Status"],
    parcels.map(p => [
      p.tracking,
      `$${Number(p.price).toFixed(2)}`,
      fmtDate(getParcelCreatedAt(p)),
      p.status
    ])
  );
}

/* ===== init ===== */
export default function initReportsPage() {
  console.log("Reports JS loaded");

  populateFilterSelects();

  document.querySelectorAll("[data-report]").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.report;

      if (key === "employees_all") return reportAllEmployees();
      if (key === "clients_all") return reportAllClients();
      if (key === "parcels_all") return reportAllParcels();
      if (key === "pending_deliveries") return reportPendingDeliveries();
      if (key === "parcels_by_employee") return askEmployeeThenReport();
      if (key === "income_period") return askIncomePeriod();
    });
  });

  qs("reportModalCloseBtn")?.addEventListener("click", closeModal);
  qs("reportModalCancelBtn")?.addEventListener("click", closeModal);

  modal()?.addEventListener("click", e => {
    if (e.target?.dataset?.close) closeModal();
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && modal()?.classList.contains("open")) {
      closeModal();
    }
  });

  qs("reportModalForm")?.addEventListener("submit", e => {
    e.preventDefault();
    const mode = qs("reportModalForm").dataset.mode;

    if (mode === "parcels_by_employee") {
      const email = qs("modalEmployeeSelect")?.value;
      if (!email) return alert("Select employee.");
      closeModal();
      return runParcelsByEmployee(email);
    }

    if (mode === "income_period") {
      const from = qs("modalFrom")?.value;
      const to = qs("modalTo")?.value;
      if (!from || !to) return alert("Select both dates.");
      closeModal();
      return runIncomePeriod(from, to);
    }
  });
}
