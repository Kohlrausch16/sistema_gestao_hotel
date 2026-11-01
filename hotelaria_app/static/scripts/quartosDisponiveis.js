const entrada = document.getElementById("id_data_entrada");
const saida = document.getElementById("id_data_saida");
const quarto = document.getElementById("id_quarto");
const mensagem = document.getElementById("mensagem-disponibilidade");
const url = document.querySelector("[data-disponibilidade-url]")?.dataset.disponibilidadeUrl;

if (entrada && saida && quarto && mensagem && url) {
    let consultaAtual;

    async function atualizarQuartos() {
        const selecaoAnterior = quarto.value || quarto.dataset.selecaoInicial || "";
        delete quarto.dataset.selecaoInicial;
        consultaAtual?.abort();
        quarto.replaceChildren(new Option("Selecione as datas primeiro", ""));
        quarto.disabled = true;

        if (!entrada.value || !saida.value) {
            mensagem.textContent = "Informe a entrada e a saída para ver os quartos disponíveis.";
            return;
        }

        if (saida.value <= entrada.value) {
            mensagem.textContent = "A saída deve ser posterior à entrada.";
            return;
        }

        const controller = new AbortController();
        consultaAtual = controller;
        mensagem.textContent = "Buscando quartos disponíveis...";

        try {
            const parametros = new URLSearchParams({
                entrada: entrada.value,
                saida: saida.value,
            });
            const resposta = await fetch(`${url}?${parametros}`, { signal: controller.signal });
            const dados = await resposta.json();
            if (!resposta.ok) throw new Error(dados.erro || "Não foi possível consultar os quartos.");

            quarto.replaceChildren(new Option("Selecione um quarto", ""));
            for (const disponivel of dados.quartos) {
                quarto.add(new Option(`${disponivel.numero} - ${disponivel.tipo}`, disponivel.id));
            }
            if (dados.quartos.some((disponivel) => String(disponivel.id) === selecaoAnterior)) {
                quarto.value = selecaoAnterior;
            }
            quarto.disabled = dados.quartos.length === 0;
            mensagem.textContent = dados.quartos.length
                ? ""
                : "Nenhum quarto disponível nesse período.";
        } catch (erro) {
            if (erro.name !== "AbortError") {
                mensagem.textContent = erro.message;
            }
        }
    }

    quarto.dataset.selecaoInicial = quarto.value;
    entrada.addEventListener("change", atualizarQuartos);
    saida.addEventListener("change", atualizarQuartos);
    atualizarQuartos();
}
