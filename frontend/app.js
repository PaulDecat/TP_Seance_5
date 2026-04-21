async function upload() {
  const file = document.getElementById("file").files[0];

  const formData = new FormData();
  formData.append("file", file);

  await fetch("http://localhost:8000/upload", {
    method: "POST",
    body: formData
  });

  alert("Fichier uploadé");
}


async function loadKPI() {
  const res = await fetch("http://localhost:8000/kpi/revenue");
  const data = await res.json();

  const display = document.getElementById("kpi");

  if (data.error) {
    display.textContent = data.error;
  } else {
    display.textContent = "CA total : " + data.total_revenue + " €";
  }
}