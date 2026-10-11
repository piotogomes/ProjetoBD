async function fetchImpressos() {
    const url = "http://127.0.0.1:8000/impressos";
    try {
        const response = await fetch(url);
        const data = await response.json();
        tableBody = document.getElementById('impressos-body')
        tableBody.innerHTML = '';
        data.forEach(impresso => {
            const row = document.createElement('tr');
            row.innerHTML = `
                        <td>${impresso.grafica_id}</td>
                        <td>${impresso.lisbn}</td>
                        <td>${new Date(impresso.data_entrega).toLocaleDateString()}</td>
                    `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
    }
}
// Chama a função para buscar os dados
fetchImpressos();

