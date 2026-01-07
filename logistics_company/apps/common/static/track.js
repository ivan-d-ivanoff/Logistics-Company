// track.js
import { getParcels } from "./storage.js";

export default function initTrackPage() {
  console.log("Track JS loaded");

  const input = document.getElementById("trackingInput");
  const btn = document.getElementById("trackingBtn");
  const result = document.getElementById("trackingResult");

  if (!input || !btn || !result) return;

  btn.addEventListener("click", () => {
    const value = input.value.trim();

    if (!value) {
      result.textContent = "Please enter tracking number.";
      return;
    }

    const parcels = getParcels();
    const parcel = parcels.find(p => p.tracking === value);

    if (!parcel) {
      result.textContent = "No parcel found with this tracking number.";
      return;
    }

    const historyText = (parcel.history || [])
      .map(h => `${new Date(h.date).toLocaleString()} – ${h.status}`)
      .join("<br>");

    result.innerHTML = `
      <strong>${parcel.tracking}</strong><br/>
      Status: ${parcel.status}<br/>
      From: ${parcel.sender} → To: ${parcel.recipient}<br/>
      Delivery: ${parcel.deliveryType},
      Weight: ${parcel.weight},
      Price: $${parcel.price.toFixed(2)}<br/><br/>
      <strong>History:</strong><br/>
      ${historyText || "No history available"}
    `;
  });
}
