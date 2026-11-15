const formularioPesquisaClientes = document.querySelector(".pesquisa-clientes");

if (formularioPesquisaClientes) {
    const campoPesquisa = formularioPesquisaClientes.querySelector("input");
    const linhas = document.querySelectorAll(".linha-cliente");
    const avisoVazio = document.querySelector(".nenhum-cliente-encontrado");

    const filtrarClientes = () => {
        const pesquisa = campoPesquisa.value.trim().toLocaleLowerCase("pt-BR");
        const cpfPesquisado = pesquisa.replace(/\D/g, "");
        let encontrados = 0;

        linhas.forEach((linha) => {
            const nome = linha.querySelector(".nome-cliente").textContent.toLocaleLowerCase("pt-BR");
            const cpf = linha.querySelector(".cpf-cliente").textContent.replace(/\D/g, "");
            linha.hidden = !nome.includes(pesquisa) && !(cpfPesquisado && cpf.includes(cpfPesquisado));
            if (!linha.hidden) encontrados += 1;
        });

        avisoVazio.hidden = encontrados > 0;
    };

    formularioPesquisaClientes.addEventListener("submit", (evento) => {
        evento.preventDefault();
        filtrarClientes();
    });
    campoPesquisa.addEventListener("input", filtrarClientes);
}
