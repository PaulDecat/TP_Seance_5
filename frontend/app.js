async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const success = document.getElementById("success");
  const error = document.getElementById("error");

  success.textContent = "";
  error.textContent = "";

  const file = fileInput.files[0];

  if (!file) {
    error.textContent = "Veuillez sélectionner un fichier";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      error.textContent = data.detail; // message backend
    } else {
      success.textContent = "Fichier importé avec succès";
    }

  } catch (e) {
    error.textContent = "Impossible de contacter le serveur";
  }
}