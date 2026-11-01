
const senha = document.getElementById("senha");
const toggleSenha = document.getElementById("toggleSenha");

toggleSenha.addEventListener("click", () => {

    const senhaVisivel = senha.type === "text";

    senha.type = senhaVisivel ? "password" : "text";

    toggleSenha.textContent = senhaVisivel
        ? "Mostrar"
        : "Ocultar";

});
