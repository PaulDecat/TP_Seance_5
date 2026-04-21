// src/utils/fileValidator.js

// Validation du fichier (format + taille)
export function validateFile(file) {
  if (!file.name.endsWith(".csv")) {
    throw new Error("Seuls les fichiers CSV sont autorisés");
  }

  const maxSize = 2 * 1024 * 1024; // 2MB
  if (file.size > maxSize) {
    throw new Error("Fichier trop volumineux");
  }
}


// Vérification contenu dangereux
export function checkDangerousContent(data) {
  const patterns = ["<script>", "DROP", "SELECT"];

  data.forEach((row) => {
    Object.values(row).forEach((value) => {
      patterns.forEach((pattern) => {
        if (value.toString().includes(pattern)) {
          throw new Error("Contenu dangereux détecté");
        }
      });
    });
  });
}