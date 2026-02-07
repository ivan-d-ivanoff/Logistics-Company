// sidebar.js
import { getCurrentUser, logout } from "./storage.js";

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function initSidebar(activeNav) {
  console.log("Sidebar JS loaded");

  const sidebar = document.querySelector(".sidebar");
  if (!sidebar) return;

  const user = getCurrentUser();
  if (!user) {
    window.location = "accounts.html";
    return;
  }

  const emailEl = document.getElementById("sidebarUserEmail");
  const roleEl = document.getElementById("sidebarUserRole");

  if (emailEl) emailEl.textContent = user.email;
  if (roleEl) roleEl.textContent = capitalize(user.role);

  document.querySelectorAll(".sidebar-link").forEach(link => {
    if (link.dataset.nav === activeNav) {
      link.classList.add("active");
    }
  });

  if (user.role === "client") {
    document.querySelectorAll(".sidebar-link").forEach(link => {
      if (!["dashboard", "parcels"].includes(link.dataset.nav)) {
        link.parentElement.style.display = "none";
      }
    });
  }

  const logoutLink = document.getElementById("logoutLink");
  if (logoutLink) {
    logoutLink.addEventListener("click", e => {
      e.preventDefault();
      logout();
    });
  }
}
