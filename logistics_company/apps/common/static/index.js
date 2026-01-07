// index.js – main JS controller

import { seedDemoData } from "./storage.js";
import initAuthPage from "./auth.js";
import initTrackPage from "./track.js";
import initSidebar from "./sidebar.js";
import initDashboardPage from "./dashboard.js";
import initParcelsPage from "./parcels.js";
import initEmployeesPage from "./employees.js";
import initOfficesPage from "./offices.js";
import initClientsPage from "./clients.js";
import initReportsPage from "./reports.js";

document.addEventListener("DOMContentLoaded", () => {
  console.log("Main JS loaded");

  // 1️⃣ Seed demo data (само веднъж)
  seedDemoData();

  // 2️⃣ Определи страницата
  const page = document.body.dataset.page;

  // 3️⃣ Public pages (без sidebar)
  if (page === "auth") {
    initAuthPage();
    return;
  }

  if (page === "track") {
    initTrackPage();
    return;
  }

  // 4️⃣ App pages (с sidebar)
  if (!page) return;

  initSidebar(page);

  switch (page) {
    case "dashboard":
      initDashboardPage();
      break;

    case "parcels":
      initParcelsPage();
      break;

    case "employees":
      initEmployeesPage();
      break;

    case "clients":
      initClientsPage();
      break;

    case "offices":
      initOfficesPage();
      break;

    case "reports":
      initReportsPage();
      break;

    default:
      console.warn("Unknown page:", page);
  }
});
