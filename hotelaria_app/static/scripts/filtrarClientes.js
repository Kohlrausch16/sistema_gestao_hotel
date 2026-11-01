const pesquisaCliente = document.getElementById("pesquisa-cliente");
const seletorCliente = document.getElementById("id_cliente");

if (pesquisaCliente && seletorCliente) {
    const opcoes = Array.from(seletorCliente.options, (opcao) => ({
        valor: opcao.value,
        texto: opcao.textContent,
        cpf: opcao.textContent.split("CPF: ")[1] || "",
    }));

    pesquisaCliente.addEventListener("input", () => {
        const cpfPesquisado = pesquisaCliente.value.replace(/\D/g, "");
        const clienteSelecionado = seletorCliente.value;
        const opcoesFiltradas = opcoes
            .filter((opcao) => !opcao.valor || opcao.cpf.includes(cpfPesquisado))
            .map((opcao) => new Option(
                opcao.texto,
                opcao.valor,
                false,
                opcao.valor === clienteSelecionado
            ));

        seletorCliente.replaceChildren(...opcoesFiltradas);
    });
}
