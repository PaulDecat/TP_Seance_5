export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://localhost:5000/upload", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.error);
  } else {
    alert("Upload OK");
    console.log(data.data);
  }
}
