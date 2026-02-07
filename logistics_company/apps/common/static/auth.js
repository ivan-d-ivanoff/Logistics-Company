// auth.js
import {
  getUsers,
  saveUsers,
  setCurrentUser,
  getClients,
  saveClients
} from "./storage.js";

export default function initAuthPage() {
  console.log("Auth JS loaded");

  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const loginTab = document.querySelector("[data-tab='login']");
  const registerTab = document.querySelector("[data-tab='register']");

  if (!loginForm || !registerForm || !loginTab || !registerTab) {
    return;
  }

  loginTab.addEventListener("click", () => {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
    loginForm.style.display = "block";
    registerForm.style.display = "none";
  });

  registerTab.addEventListener("click", () => {
    registerTab.classList.add("active");
    loginForm.style.display = "none";
    registerForm.style.display = "block";
  });

  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = loginForm.querySelector("input[name='email']").value.trim();
    const password = loginForm.querySelector("input[name='password']").value;

    const users = getUsers();
    const user = users.find(
      (u) => u.email === email && u.password === password
    );

    if (!user) {
      alert("Invalid email or password.");
      return;
    }

    setCurrentUser(user);

    window.location.href = "/dashboard/";
  });

  registerForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const fullName = registerForm
      .querySelector("input[name='fullName']")
      .value.trim();
    const email = registerForm
      .querySelector("input[name='email']")
      .value.trim();
    const password = registerForm
      .querySelector("input[name='password']")
      .value;

    if (!fullName || !email || !password) {
      alert("Please fill all fields.");
      return;
    }

    const users = getUsers();
    if (users.some((u) => u.email === email)) {
      alert("User with this email already exists.");
      return;
    }

    const newUser = {
      id: Date.now(),
      name: fullName,
      email,
      password,
      role: "client"
    };

    users.push(newUser);
    saveUsers(users);

    const clients = getClients();
    if (!clients.some((c) => c.email === email)) {
      clients.push({
        id: Date.now(),
        name: fullName,
        email,
        phone: ""
      });
      saveClients(clients);
    }

    setCurrentUser(newUser);
    alert("Account created as Client. You are now logged in.");

    window.location.href = "/dashboard/";
  });
}
