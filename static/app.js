const form = document.getElementById("upload-form");
const input = document.getElementById("file-input");
const button = document.getElementById("submit-btn");
const message = document.getElementById("message");
const chartMessage = document.getElementById("chart-message");
const chartCanvas = document.getElementById("segment-chart");
const refreshChartButton = document.getElementById("refresh-chart-btn");
const chartContext = chartCanvas.getContext("2d");


function showMessage(text, isSuccess) {
  message.textContent = text;
  message.classList.remove("success", "error");
  message.classList.add(isSuccess ? "success" : "error");
}


function setChartMessage(text) {
  chartMessage.textContent = text;
}

function clearChart() {
  chartContext.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
}

function drawSegmentChart(segments, totalClients) {
  clearChart();
  if (!segments.length || totalClients === 0) {
    setChartMessage("Aucune donnee a afficher pour le moment.");
    return;
  }

  const padding = 32;
  const rowHeight = 42;
  const barAreaWidth = chartCanvas.width - (padding * 2 + 180);
  const maxCount = Math.max(...segments.map((segment) => segment.count));
  const colors = ["#1f6feb", "#0ea5e9", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#06b6d4"];

  chartContext.fillStyle = "#111827";
  chartContext.font = "14px Arial";
  chartContext.fillText(`Total clients: ${totalClients}`, padding, 18);

  segments.forEach((segment, index) => {
    const y = padding + index * rowHeight;
    const label = segment.label.length > 18 ? `${segment.label.slice(0, 18)}...` : segment.label;
    const barWidth = maxCount > 0 ? Math.round((segment.count / maxCount) * barAreaWidth) : 0;
    const color = colors[index % colors.length];

    chartContext.fillStyle = "#374151";
    chartContext.fillText(label, padding, y);

    chartContext.fillStyle = color;
    chartContext.fillRect(padding + 130, y - 12, barWidth, 16);

    chartContext.fillStyle = "#111827";
    chartContext.fillText(
      `${segment.count} (${segment.percentage.toFixed(1)}%)`,
      padding + 136 + barWidth,
      y
    );
  });
}

async function loadSegmentChart() {
  refreshChartButton.disabled = true;
  setChartMessage("Chargement de la repartition...");
  try {
    const response = await fetch("/api/segments");
    const payload = await response.json();
    if (!payload || !Array.isArray(payload.segments)) {
      setChartMessage("Impossible de recuperer les segments.");
      clearChart();
      return;
    }

    if (!payload.ok) {
      setChartMessage(payload.message || "Aucune donnee segmentable disponible.");
      clearChart();
      return;
    }

    drawSegmentChart(payload.segments, payload.total_clients || 0);
    setChartMessage("Graphique mis a jour.");
  } catch (error) {
    setChartMessage("Erreur reseau lors du chargement du graphique.");
    clearChart();
  } finally {
    refreshChartButton.disabled = false;
  }
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = input.files[0];
  if (!file) {
    showMessage("Veuillez selectionner un fichier CSV.", false);
    return;
  }

  if (!file.name.toLowerCase().endsWith(".csv")) {
    showMessage("Erreur: seuls les fichiers CSV sont acceptes.", false);
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  button.disabled = true;
  showMessage("Upload en cours...", true);

  try {
    const response = await fetch("/api/import", {
      method: "POST",
      body: formData,
    });
    let payload = null;
    try {
      payload = await response.json();
    } catch (parseError) {
      payload = null;
    }

    if (response.status === 413) {
      showMessage("Fichier trop volumineux. Taille maximale autorisee: 50 Mo.", false);
      return;
    }

    if (!payload) {
      showMessage("Reponse serveur invalide.", false);
      return;
    }

    showMessage(payload.message, Boolean(payload.ok));
    if (payload.ok) {
      form.reset();

      await loadSegmentChart();ain
    }
  } catch (error) {
    showMessage("Erreur reseau pendant l'upload.", false);
  } finally {
    button.disabled = false;
  }
});

refreshChartButton.addEventListener("click", () => {
  loadSegmentChart();
});

loadSegmentChart();ain
