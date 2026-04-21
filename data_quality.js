function renderTable(data) {
  const table = document.createElement("table");

  const headers = Object.keys(data[0]);

  table.innerHTML = `
    <tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>
    ${data.slice(0, 10).map(row =>
      `<tr>${headers.map(h => `<td>${row[h]}</td>`).join("")}</tr>`
    ).join("")}
  `;

  document.body.appendChild(table);
}