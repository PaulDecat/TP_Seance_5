const form = document.getElementById("upload-form");
const input = document.getElementById("file-input");
const button = document.getElementById("submit-btn");
const message = document.getElementById("message");

const riskCount = document.getElementById("risk-count");
const totalCount = document.getElementById("total-count");
const recommendationsList = document.getElementById("recommendations-list");
const actionsList = document.getElementById("actions-list");


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

function renderActions(actions) {
  actionsList.innerHTML = "";
  if (!actions.length) {
    const item = document.createElement("li");
    item.textContent = "Aucune action creee pour le moment.";
    actionsList.appendChild(item);
    return;
  }

  actions.forEach((action) => {
    const item = document.createElement("li");
    item.textContent = `${action.action_title} - ${action.recommendation_title}`;
    actionsList.appendChild(item);
  });
}

function buildRecommendationCard(recommendation) {
  const card = document.createElement("article");
  card.className = "recommendation-card";

  const title = document.createElement("h3");
  title.textContent = recommendation.title;

  const description = document.createElement("p");
  description.textContent = recommendation.description;

  const actionForm = document.createElement("form");
  actionForm.className = "action-form";

  const input = document.createElement("input");
  input.type = "text";
  input.className = "action-input";
  input.placeholder = "Nom de l'action";
  input.required = true;

  const submitButton = document.createElement("button");
  submitButton.type = "submit";
  submitButton.textContent = "Creer une action";

  actionForm.appendChild(input);
  actionForm.appendChild(submitButton);

  actionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const actionTitle = input.value.trim();
    if (!actionTitle) {
      showMessage("Veuillez saisir un nom d'action.", false);
      return;
    }

    submitButton.disabled = true;
    try {
      const response = await fetch("/api/actions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recommendation_id: recommendation.id,
          action_title: actionTitle,
        }),
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        showMessage(payload.message || "Erreur lors de la creation de l'action.", false);
        return;
      }

      showMessage(payload.message, true);
      input.value = "";
      await loadRecommendationsAndActions();
    } catch (error) {
      showMessage("Erreur reseau lors de la creation de l'action.", false);
    } finally {
      submitButton.disabled = false;
    }
  });

  card.appendChild(title);
  card.appendChild(description);
  card.appendChild(actionForm);
  return card;
}

async function loadRecommendationsAndActions() {
  try {
    const response = await fetch("/api/recommendations");
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error("Invalid response");
    }

    recommendationsList.innerHTML = "";
    payload.recommendations.forEach((recommendation) => {
      recommendationsList.appendChild(buildRecommendationCard(recommendation));
    });
    renderActions(payload.actions);
  } catch (error) {
    recommendationsList.innerHTML = "";
    actionsList.innerHTML = "";
    const errorItem = document.createElement("li");
    errorItem.textContent = "Impossible de charger les recommandations et actions.";
    actionsList.appendChild(errorItem);
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
loadRecommendationsAndActions();
