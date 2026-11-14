document.querySelectorAll("button.botao-cancelar").forEach((botao) => {
    botao.addEventListener("click", () => {
        window.location.reload();
    });
});
