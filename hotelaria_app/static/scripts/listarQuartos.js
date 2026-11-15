document.querySelectorAll('.botao-reservas').forEach((botao) => {
    botao.addEventListener('click', () => {
        document.getElementById(botao.dataset.dialogId).showModal();
    });
});

document.querySelectorAll('.dialogo-reservas').forEach((dialogo) => {
    dialogo.querySelector('.fechar-dialogo-reservas').addEventListener('click', () => {
        dialogo.close();
    });

    dialogo.addEventListener('click', (evento) => {
        if (evento.target === dialogo) {
            dialogo.close();
        }
    });
});
