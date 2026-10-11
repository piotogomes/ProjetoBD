async function fetchLivros() {
    const url = "http://127.0.0.1:8000/livros";
    const response = await fetch(url);
    return await response.json();
}

async function fetchLivrosComFiltro() {
    const url = new URL("http://127.0.0.1:8000/livros");
    const params = new URLSearchParams();
    const rg = document.getElementById("filtro-rg").value
    const editora = document.getElementById("filtro-editora").value
    const livro = document.getElementById("filtro-livro").value
    if (rg) params.append("rg", rg);
    if (editora) params.append("editora", editora);
    if (livro) params.append("livro", livro);
    url.search = params.toString();
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        alert('Erro ao buscar livros');
    }
}

async function loadFiltros() {
    try {
        const livros = await fetchLivros()
        const rgSelect = document.getElementById("filtro-rg")
        const editoraSelect = document.getElementById("filtro-editora")
        const isbnSelect = document.getElementById("filtro-livro")
        const rgsUnicos = [...new Set(livros.map(livro => livro.rg))];
        const editorasUnicas = [...new Set(livros.map(livro => livro.editora_id))];
        const isbnsUnicos = [...new Set(livros.map(livro => livro.isbn))];

        rgsUnicos.forEach(rg => {
            const option = document.createElement("option");
            option.value = rg;
            option.textContent = rg;
            rgSelect.appendChild(option);
        });

        // Preencher filtro de Editora
        editorasUnicas.forEach(editora => {
            const option = document.createElement("option");
            option.value = editora;
            option.textContent = editora;
            editoraSelect.appendChild(option);
        });

        // Preencher filtro de ISBN (Livro)
        isbnsUnicos.forEach(isbn => {
            const option = document.createElement("option");
            option.value = isbn;
            option.textContent = isbn;
            isbnSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Erro ao carregar livros:", error);
    }
}

async function loadLivros() {
    try {
        livros = await fetchLivrosComFiltro();
        books = document.getElementById('div-livros');
        books.innerHTML = '';
        livros.forEach(livro => {
            const bookDiv = document.createElement('div');
            bookDiv.classList.add('book');
            bookDiv.innerHTML = `
              <h2>${livro.titulo}</h2>
              <p><strong>Data de Publicação:</strong> ${new Date(livro.data_de_publicacao).toLocaleDateString()}</p>
              <p><strong>Editora ID:</strong> ${livro.editora_id}</p>
              <p><strong>Endereço:</strong> ${livro.endereco}</p>
              <p><strong>ID:</strong> ${livro.id}</p>
              <p><strong>ISBN:</strong> ${livro.isbn}</p>
              <p><strong>Nome do Autor:</strong> ${livro.nome}</p>
              <p><strong>RG do Autor:</strong> ${livro.rg}</p>            `;
            books.appendChild(bookDiv);
        }
        )
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
    }
}
loadLivros()
loadFiltros()
