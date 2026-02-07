// parcels.js
import { getCurrentUser, getParcels, saveParcels } from "./storage.js";

let query = "";

/* ===== helpers ===== */
function qs(id) {
  return document.getElementById(id);
}

const modal = () => qs("parcelModal");

function role() {
  return getCurrentUser()?.role || null;
}

function canRegisterOrEdit() {
  return role() === "admin" || role() === "employee";
}

function canDelete() {
  return role() === "admin";
}

function getVisibleParcels(parcels) {
  const user = getCurrentUser();
  if (!user) return [];

  if (user.role === "admin" || user.role === "employee") {
    return parcels;
  }

  return parcels.filter(p => p.ownerEmail === user.email);
}

/* ===== render helpers ===== */
function renderStatusBadge(status) {
  let cls = "badge-info";
  if (status === "In Transit") cls = "badge-warning";
  if (status === "Delivered") cls = "badge-success";
  if (status === "Returned") cls = "badge-danger";
  return `<span class="badge ${cls}">${status}</span>`;
}

function calcPrice(weightNumber) {
  const w = Number(weightNumber);
  if (Number.isNaN(w)) return 10;
  return 5 + 2 * w;
}

/* ===== modal helpers ===== */
function openModal(title) {
  qs("parcelModalTitle").textContent = title;
  modal().classList.add("open");
  modal().setAttribute("aria-hidden", "false");
  setTimeout(() => qs("pTracking")?.focus(), 0);
}

function closeModal() {
  modal().classList.remove("open");
  modal().setAttribute("aria-hidden", "true");
  qs("parcelForm")?.reset();
  qs("parcelId").value = "";
  qs("pPrice").value = "";
}

function fillForm(parcel) {
  qs("parcelId").value = parcel?.id ?? "";
  qs("pTracking").value = parcel?.tracking ?? "LT-2024-";
  qs("pSender").value = parcel?.sender ?? "";
  qs("pRecipient").value = parcel?.recipient ?? "";
  qs("pDeliveryType").value = parcel?.deliveryType ?? "Address";

  const weightStr = parcel?.weight
    ? String(parcel.weight).replace(" kg", "").trim()
    : "";
  qs("pWeight").value = parcel ? parseFloat(weightStr) || 0 : 1;

  qs("pStatus").value = parcel?.status ?? "Registered";

  qs("ownerEmailGroup").style.display = "block";
  qs("pOwnerEmail").value = parcel?.ownerEmail ?? "";

  const price = parcel?.price ?? calcPrice(qs("pWeight").value);
  qs("pPrice").value = `$${Number(price).toFixed(2)}`;
}

/* ===== table render ===== */
function renderParcelsTable() {
  const tbody = qs("parcelsTableBody");
  if (!tbody) return;

  const parcels = getVisibleParcels(getParcels());
  const q = query.trim().toLowerCase();

  const visible = q
    ? parcels.filter(p =>
        (p.tracking || "").toLowerCase().includes(q) ||
        (p.sender || "").toLowerCase().includes(q) ||
        (p.recipient || "").toLowerCase().includes(q)
      )
    : parcels;

  tbody.innerHTML = "";

  const allowManage = canRegisterOrEdit();
  const allowDelete = canDelete();

  visible.forEach(parcel => {
    const tr = document.createElement("tr");

    const actionsHtml = allowManage
      ? `
        <button class="btn-icon" data-action="view" data-id="${parcel.id}">👁️</button>
        <button class="btn-icon" data-action="edit" data-id="${parcel.id}">✏️</button>
        ${allowDelete ? `<button class="btn-icon" data-action="delete" data-id="${parcel.id}">🗑️</button>` : ``}
      `
      : `<button class="btn-icon" data-action="view" data-id="${parcel.id}">👁️</button>`;

    tr.innerHTML = `
      <td>${parcel.tracking}</td>
      <td>${parcel.sender}</td>
      <td>${parcel.recipient}</td>
      <td><span class="badge badge-info">${parcel.deliveryType}</span></td>
      <td>${parcel.weight}</td>
      <td>$${parcel.price.toFixed(2)}</td>
      <td>${renderStatusBadge(parcel.status)}</td>
      <td>${actionsHtml}</td>
    `;

    tbody.appendChild(tr);
  });

  const info = qs("parcelsCountInfo");
  if (info) info.textContent = `Showing ${visible.length} results`;

  const registerBtn = qs("registerParcelBtn");
  if (registerBtn) {
    registerBtn.style.display = canRegisterOrEdit() ? "inline-flex" : "none";
  }
}

/* ===== actions ===== */
function getParcelById(id) {
  return getParcels().find(p => p.id === id);
}

function viewParcel(id) {
  const parcel = getParcelById(id);
  if (!parcel) return;

  const user = getCurrentUser();
  if (user?.role === "client" && parcel.ownerEmail !== user.email) {
    alert("You can view only your own parcels.");
    return;
  }

  const historyText = (parcel.history || [])
    .map(h => `${new Date(h.date).toLocaleString()} – ${h.status}`)
    .join("\n");

  alert(
`Tracking: ${parcel.tracking}
From: ${parcel.sender}
To: ${parcel.recipient}
Delivery: ${parcel.deliveryType}
Weight: ${parcel.weight}
Price: $${parcel.price.toFixed(2)}
Status: ${parcel.status}

History:
${historyText || "(no history)"}`
  );
}

function openAddParcel() {
  if (!canRegisterOrEdit()) {
    alert("Clients cannot register parcels.");
    return;
  }
  fillForm(null);
  openModal("Register Parcel");
}

function openEditParcel(id) {
  if (!canRegisterOrEdit()) {
    alert("Clients cannot edit parcels.");
    return;
  }

  const parcels = getParcels();
  const parcel = parcels.find(p => p.id === id);
  if (!parcel) return;

  fillForm(parcel);
  openModal("Edit Parcel");
}

function deleteParcel(id) {
  if (!canDelete()) {
    alert("Only admin can delete parcels.");
    return;
  }

  const parcels = getParcels();
  const idx = parcels.findIndex(p => p.id === id);
  if (idx === -1) return;

  if (!confirm("Delete this parcel?")) return;

  parcels.splice(idx, 1);
  saveParcels(parcels);
  renderParcelsTable();
}

/* ===== form submit ===== */
function onSaveParcel(e) {
  e.preventDefault();

  if (!canRegisterOrEdit()) {
    alert("Clients cannot create/edit parcels.");
    return;
  }

  const idRaw = qs("parcelId").value;
  const tracking = qs("pTracking").value.trim();
  const sender = qs("pSender").value.trim();
  const recipient = qs("pRecipient").value.trim();
  const deliveryType = qs("pDeliveryType").value;
  const weightNum = Number(qs("pWeight").value);
  const status = qs("pStatus").value;
  const ownerEmail = qs("pOwnerEmail").value.trim() || null;

  if (!tracking || !sender || !recipient || !deliveryType) {
    alert("Please fill Tracking, Sender, Recipient and Delivery Type.");
    return;
  }

  if (Number.isNaN(weightNum) || weightNum <= 0) {
    alert("Weight must be a positive number.");
    return;
  }

  const price = calcPrice(weightNum);
  qs("pPrice").value = `$${price.toFixed(2)}`;

  const parcels = getParcels();

  if (idRaw) {
    const id = Number(idRaw);
    const idx = parcels.findIndex(p => p.id === id);
    if (idx === -1) return;

    const existing = parcels[idx];

    const updated = {
      ...existing,
      tracking,
      sender,
      recipient,
      deliveryType,
      price,
      ownerEmail,
      weight: `${weightNum} kg`
    };

    if (existing.status !== status) {
      updated.status = status;
      updated.history = updated.history || [];
      updated.history.push({ date: new Date().toISOString(), status });
    } else {
      updated.status = status;
    }

    parcels[idx] = updated;
    saveParcels(parcels);

    closeModal();
    renderParcelsTable();
    return;
  }

  const newParcel = {
    id: Date.now(),
    tracking,
    sender,
    ownerEmail,
    recipient,
    deliveryType,
    weight: `${weightNum} kg`,
    price,
    status: "Registered",
    history: [{ date: new Date().toISOString(), status: "Registered" }]
  };

  parcels.push(newParcel);
  saveParcels(parcels);

  closeModal();
  renderParcelsTable();
}

/* ===== init ===== */
export default function initParcelsPage() {
  console.log("Parcels JS loaded");

  const btn = qs("registerParcelBtn");
  const tbody = qs("parcelsTableBody");
  const search = qs("parcelsSearch");

  if (btn) btn.style.display = canRegisterOrEdit() ? "inline-flex" : "none";
  if (btn) btn.addEventListener("click", openAddParcel);

  if (search) {
    search.addEventListener("input", e => {
      query = e.target.value || "";
      renderParcelsTable();
    });
  }

  if (tbody) {
    tbody.addEventListener("click", e => {
      const b = e.target.closest("button[data-action]");
      if (!b) return;

      const id = Number(b.dataset.id);
      const action = b.dataset.action;

      if (action === "view") viewParcel(id);
      if (action === "edit") openEditParcel(id);
      if (action === "delete") deleteParcel(id);
    });
  }

  qs("pWeight")?.addEventListener("input", () => {
    const w = Number(qs("pWeight").value);
    qs("pPrice").value = `$${calcPrice(w).toFixed(2)}`;
  });

  qs("parcelModalCloseBtn")?.addEventListener("click", closeModal);
  qs("parcelCancelBtn")?.addEventListener("click", closeModal);

  modal()?.addEventListener("click", e => {
    if (e.target?.dataset?.close) closeModal();
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && modal()?.classList.contains("open")) {
      closeModal();
    }
  });

  qs("parcelForm")?.addEventListener("submit", onSaveParcel);

  renderParcelsTable();
}
