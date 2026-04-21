export async function createAction(action) {
  await fetch("http://localhost:5000/actions", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(action)
  });
}