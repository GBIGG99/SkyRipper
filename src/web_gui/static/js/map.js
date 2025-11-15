const DEFAULT_GEO = window.SKYRIPPER_DEFAULT_GEO || {
  lat: 0,
  lon: 0,
  radius: 250,
};

const map = L.map("map", {
  zoomControl: true,
}).setView([DEFAULT_GEO.lat, DEFAULT_GEO.lon], 15);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const detectionLayer = L.layerGroup().addTo(map);
const deviceLayer = L.layerGroup().addTo(map);

function formatTimestamp(ts) {
  return new Date(ts * 1000).toLocaleTimeString();
}

function renderDetections(detections) {
  detectionLayer.clearLayers();
  const lines = detections.map((det) => {
    const label = `${det.frequency_mhz.toFixed(2)} MHz`;
    const popup = `Frequency: ${det.frequency_mhz.toFixed(2)} MHz\nPower: ${det.power_dbm.toFixed(1)} dBm\nConfidence: ${(det.confidence * 100).toFixed(0)}%`;
    const latOffset = (Math.random() - 0.5) * 0.005;
    const lonOffset = (Math.random() - 0.5) * 0.005;
    const marker = L.circleMarker([DEFAULT_GEO.lat + latOffset, DEFAULT_GEO.lon + lonOffset], {
      radius: 8,
      color: "#f97316",
      fillColor: "#fb923c",
      fillOpacity: 0.7,
    }).bindTooltip(popup.replace(/\n/g, "<br />"));
    detectionLayer.addLayer(marker);
    return `${formatTimestamp(det.timestamp)} | ${label} | ${(det.confidence * 100).toFixed(0)}%`;
  });
  document.getElementById("detections-log").textContent = lines.join("\n") || "No detections yet";
}

function renderDevices(devices) {
  deviceLayer.clearLayers();
  const lines = devices.map((device) => {
    if (device.lat && device.lon) {
      const marker = L.marker([device.lat, device.lon]).bindTooltip(
        `${device.ssid || "Unknown"} (${device.mac})`
      );
      deviceLayer.addLayer(marker);
    }
    return `${device.mac} | ${device.ssid || "(hidden)"}`;
  });
  document.getElementById("devices-log").textContent = lines.join("\n") || "No active devices";
}

async function refresh() {
  try {
    const [detectionsRes, devicesRes] = await Promise.all([
      fetch("/api/detections"),
      fetch("/api/kismet"),
    ]);
    const detectionsJson = await detectionsRes.json();
    const devicesJson = await devicesRes.json();
    renderDetections(detectionsJson.detections || []);
    renderDevices(devicesJson.devices || []);
  } catch (error) {
    console.error("Failed to refresh data", error);
  }
}

refresh();
setInterval(refresh, 5000);
