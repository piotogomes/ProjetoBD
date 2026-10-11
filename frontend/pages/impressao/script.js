async function fetchLivros() {
    try {
        const response = await fetch('http://127.0.0.1:8000/livros');
        const data = await response.json();
        const livroSelect = document.getElementById("livro");
        data.forEach(livro => {
            const option = document.createElement("option");
            option.value = livro.isbn;  // Usando o ID do livro como valor
            option.textContent = livro.titulo;  // Exibindo o nome do livro
            livroSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Erro ao carregar livros:", error);
    }
}

async function fetchGraficas() {
    try {
        const response = await fetch('http://127.0.0.1:8000/grafica');
        const data = await response.json();
        const graficaSelect = document.getElementById("grafica");
        data.forEach(grafica => {
            const option = document.createElement("option");
            option.value = grafica.id;  // Usando o ID da gráfica como valor
            option.textContent = grafica.nome;  // Exibindo o nome da gráfica
            graficaSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Erro ao carregar gráficas:", error);
    }
}

fetchLivros();
fetchGraficas();

async function enviarParaImpressao() {
    const livro = document.getElementById("livro").value;
    const grafica = document.getElementById("grafica").value;
    const copias = document.getElementById("input-copias").value;
    const data = document.getElementById("input-data").value;

    if (!livro || !grafica || !copias || !data) {
        alert("Por favor, preencha todos os campos.");
        return;
    }

    // Criando o objeto JSON para enviar
    const dataToSend = {
        isbn: livro,      // O valor do livro
        grafica: grafica, // O valor da gráfica
        copias: copias,  // Número de cópias
        data: data        // Data no formato YYYY-MM-DD
    };
    console.log(dataToSend)

    // Enviando a requisição POST
    try {
        const response = await fetch('http://localhost:8000/impressos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
        });

        if (!response.ok) {
            throw new Error(`Erro ao enviar a solicitação de impressão: ${response.statusText}`);
        }
        alert('Impressão solicitada com sucesso!');
    } catch (error) {
        alert('Erro ao enviar a solicitação de impressão.');
    }
}
