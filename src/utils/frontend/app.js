import { uploadFile } from "./components/upload.js";

fetch("http://localhost:5000/ca")
  .then((r) => r.json())
  .then(data => {
    document.getElementById("ca").innerText = data.ca;
  });

document.getElementById("upload-btn").addEventListener("click", () => {
  const file = document.getElementById("file").files[0];
  if (!file) {
    alert("Veuillez selectionner un fichier.");
    return;
  }

  uploadFile(file);
});