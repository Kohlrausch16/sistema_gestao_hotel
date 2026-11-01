
document.querySelectorAll(".botao-retornar").forEach((botao) => {
    botao.addEventListener("click", () => {
        const origemAnterior = document.referrer
            ? new URL(document.referrer).origin
            : null;

        if (origemAnterior === window.location.origin && window.history.length > 1) {
            window.history.back();
        } else {
            window.location.assign(document.body.dataset.homeUrl);
        }
    });
});
