// fetch devices and render
async function loadDevices() {
  const res = await fetch("/api/devices");
  const devices = await res.json();
  const container = document.getElementById("devices");
  container.innerHTML = "";
  const tpl = document.getElementById("device-tpl");

  devices.forEach(d => {
    const node = tpl.content.cloneNode(true);
    node.querySelector("[data-name]").textContent = d.name;
    node.querySelector("[data-id]").textContent = d.id;
    const statusEl = node.querySelector("[data-status]");
    statusEl.textContent = d.status || "unknown";
    statusEl.className = d.status === "online"
      ? "text-sm px-3 py-1 rounded-full text-white bg-green-600"
      : "text-sm px-3 py-1 rounded-full text-white bg-gray-500";

    const btn = node.querySelector(".send-command");
    btn.addEventListener("click", () => sendCommand(d.id));

    container.appendChild(node);
  });
}

async function sendCommand(deviceId) {
  const payload = { command: "ping", params: { ts: Date.now() } };
  const res = await fetch(`/api/devices/${deviceId}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  alert(`Command sent: ${JSON.stringify(data)}`);
}

document.addEventListener("DOMContentLoaded", () => {
  loadDevices();
});