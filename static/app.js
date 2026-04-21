const form = document.getElementById("upload-form");
const input = document.getElementById("file-input");
const button = document.getElementById("submit-btn");
const message = document.getElementById("message");

const riskCount = document.getElementById("risk-count");
const totalCount = document.getElementById("total-count");


function showMessage(text, isSuccess) {
  message.textContent = text;
  message.classList.remove("success", "error");
  message.classList.add(isSuccess ? "success" : "error");
}
async function refreshRiskCount() {
  try {
    const response = await fetch("/api/risk-clients");
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error("Invalid response");
    }

    riskCount.textContent = String(payload.risk_clients);
    totalCount.textContent = String(payload.total_clients);
  } catch (error) {
    riskCount.textContent = "-";
    totalCount.textContent = "-";
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

      await refreshRiskCount();
    }
  } catch (error) {
    showMessage("Erreur reseau pendant l'upload.", false);
  } finally {
    button.disabled = false;
  }
});

refreshRiskCount();
