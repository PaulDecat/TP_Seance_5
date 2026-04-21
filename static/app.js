const form = document.getElementById("upload-form");
const input = document.getElementById("file-input");
const button = document.getElementById("submit-btn");
const message = document.getElementById("message");

function showMessage(text, isSuccess) {
  message.textContent = text;
  message.classList.remove("success", "error");
  message.classList.add(isSuccess ? "success" : "error");
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
    }
  } catch (error) {
    showMessage("Erreur reseau pendant l'upload.", false);
  } finally {
    button.disabled = false;
  }
});
