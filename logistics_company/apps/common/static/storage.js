// storage.js
console.log("Storage JS loaded");

// ---------- DEMO SEED DATA ----------

const SEED_EMPLOYEES = [
  { id: 1, name: "Michael Roberts", email: "m.roberts@logitrack.com", role: "Courier", office: "Downtown Office", phone: "+1 (555) 111-2222" },
  { id: 2, name: "Sarah Chen", email: "s.chen@logitrack.com", role: "Office Staff", office: "Westside Branch", phone: "+1 (555) 222-3333" },
  { id: 3, name: "James Wilson", email: "j.wilson@logitrack.com", role: "Courier", office: "Central Hub", phone: "+1 (555) 333-4444" },
  { id: 4, name: "Emma Davis", email: "e.davis@logitrack.com", role: "Office Staff", office: "Downtown Office", phone: "+1 (555) 444-5555" },
  { id: 5, name: "Robert Taylor", email: "r.taylor@logitrack.com", role: "Courier", office: "Tech District", phone: "+1 (555) 555-6666" },
  { id: 6, name: "Lisa Anderson", email: "l.anderson@logitrack.com", role: "Office Staff", office: "Harbor Point", phone: "+1 (555) 666-7777" }
];

const SEED_PARCELS = [
  {
    id: 1,
    tracking: "LT-2024-001234",
    sender: "John Smith",
    ownerEmail: "john@example.com",
    recipient: "Jane Doe",
    deliveryType: "Address",
    weight: "2.5 kg",
    price: 15.99,
    status: "In Transit",
    history: [{ date: new Date().toISOString(), status: "In Transit" }]
  },
  {
    id: 2,
    tracking: "LT-2024-001235",
    sender: "Alice Brown",
    ownerEmail: "alice@example.com",
    recipient: "Bob Wilson",
    deliveryType: "Office",
    weight: "1.2 kg",
    price: 8.5,
    status: "Delivered",
    history: [{ date: new Date().toISOString(), status: "Delivered" }]
  }
];

const SEED_OFFICES = [
  { id: 1, name: "Downtown Office", city: "Sofia", address: "Main St 1", phone: "+359 2 111 1111" },
  { id: 2, name: "Westside Branch", city: "Sofia", address: "West Blvd 23", phone: "+359 2 222 2222" }
];

const SEED_CLIENTS = [
  { id: 1, name: "John Smith", email: "john@example.com", phone: "+1 (555) 111-0000" },
  { id: 2, name: "Alice Brown", email: "alice@example.com", phone: "+1 (555) 222-0000" }
];


export function getUsers() {
  return JSON.parse(localStorage.getItem("users") || "[]");
}

export function saveUsers(users) {
  localStorage.setItem("users", JSON.stringify(users));
}

export function getParcels() {
  return JSON.parse(localStorage.getItem("parcels") || "[]");
}

export function saveParcels(parcels) {
  localStorage.setItem("parcels", JSON.stringify(parcels));
}

export function getEmployees() {
  return JSON.parse(localStorage.getItem("employees") || "[]");
}

export function saveEmployees(employees) {
  localStorage.setItem("employees", JSON.stringify(employees));
}

export function getOffices() {
  return JSON.parse(localStorage.getItem("offices") || "[]");
}

export function saveOffices(offices) {
  localStorage.setItem("offices", JSON.stringify(offices));
}

export function getClients() {
  return JSON.parse(localStorage.getItem("clients") || "[]");
}

export function saveClients(clients) {
  localStorage.setItem("clients", JSON.stringify(clients));
}

export function getCurrentUser() {
  return JSON.parse(localStorage.getItem("currentUser") || "null");
}

export function setCurrentUser(user) {
  localStorage.setItem("currentUser", JSON.stringify(user));
}

export function logout() {
  localStorage.removeItem("currentUser");
  window.location = "/";
}

// ---------- INITIAL SEED ----------

export function seedDemoData() {
  const admin = {
    id: 1,
    name: "Admin User",
    email: "admin@logitrack.com",
    password: "admin123",
    role: "admin"
  };

  let users = getUsers();

  if (users.length === 0) {
    users = [admin];
  } else {
    const hasAdmin = users.some(u => u.email === admin.email);
    if (!hasAdmin) users.push(admin);
  }

  saveUsers(users);

  if (!localStorage.getItem("employees")) saveEmployees(SEED_EMPLOYEES);
  if (!localStorage.getItem("parcels")) saveParcels(SEED_PARCELS);
  if (!localStorage.getItem("offices")) saveOffices(SEED_OFFICES);
  if (!localStorage.getItem("clients")) saveClients(SEED_CLIENTS);
}
