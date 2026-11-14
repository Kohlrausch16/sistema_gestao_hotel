const entrada = document.getElementById("id_data_entrada");
const saida = document.getElementById("id_data_saida");
const quarto = document.getElementById("id_quarto");
const mensagem = document.getElementById("mensagem-disponibilidade");
const url = document.querySelector("[data-disponibilidade-url]")?.dataset.disponibilidadeUrl;
const reservaId = document.querySelector("[data-reserva-id]")?.dataset.reservaId;

if (entrada && saida && quarto && mensagem && url) {
    let consultaAtual;
    let quartosDisponiveis = [];
    let quartoSelecionado = quarto.value;
    const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

    function dataIso(valor) {
        const partes = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(valor.trim());
        if (!partes) return null;
        const [, dia, mes, ano] = partes;
        const data = new Date(`${ano}-${mes}-${dia}T00:00:00Z`);
        if (Number.isNaN(data.getTime()) || data.getUTCFullYear() !== Number(ano)
            || data.getUTCMonth() + 1 !== Number(mes) || data.getUTCDate() !== Number(dia)) {
            return null;
        }
        return `${ano}-${mes}-${dia}`;
    }

    function mostrarPrecoSelecionado() {
        const selecionado = quartosDisponiveis.find((item) => String(item.id) === quarto.value);
        mensagem.textContent = selecionado
            ? `Preço total da estadia: ${moeda.format(Number(selecionado.preco_total))}`
            : "Selecione um quarto para ver o preço total da estadia.";
    }

    async function atualizarQuartos() {
        const entradaIso = dataIso(entrada.value);
        const saidaIso = dataIso(saida.value);
        const selecaoAnterior = quarto.value || quartoSelecionado;
        consultaAtual?.abort();
        quarto.replaceChildren(new Option("Selecione as datas primeiro", ""));
        quarto.disabled = true;
        quartosDisponiveis = [];

        if (!entradaIso || !saidaIso) {
            mensagem.textContent = "Informe a entrada e a saída no formato dd/mm/aaaa para ver os quartos disponíveis.";
            return;
        }

        if (saidaIso <= entradaIso) {
            mensagem.textContent = "A saída deve ser posterior à entrada.";
            return;
        }

        const controller = new AbortController();
        consultaAtual = controller;
        mensagem.textContent = "Buscando quartos disponíveis...";

        try {
            const parametros = new URLSearchParams({
                entrada: entradaIso,
                saida: saidaIso,
            });
            if (reservaId) parametros.set("reserva_id", reservaId);
            const resposta = await fetch(`${url}?${parametros}`, { signal: controller.signal });
            const dados = await resposta.json();
            if (!resposta.ok) throw new Error(dados.erro || "Não foi possível consultar os quartos.");

            quartosDisponiveis = dados.quartos;
            quarto.replaceChildren(new Option("Selecione um quarto", ""));
            for (const disponivel of dados.quartos) {
                quarto.add(new Option(
                    `${disponivel.numero} - ${disponivel.tipo} - ${moeda.format(Number(disponivel.preco_total))}`,
                    disponivel.id
                ));
            }
            if (dados.quartos.some((disponivel) => String(disponivel.id) === selecaoAnterior)) {
                quarto.value = selecaoAnterior;
                quartoSelecionado = selecaoAnterior;
            } else {
                quartoSelecionado = "";
            }
            quarto.disabled = dados.quartos.length === 0;
            if (dados.quartos.length) {
                mostrarPrecoSelecionado();
            } else {
                mensagem.textContent = "Nenhum quarto disponível nesse período.";
            }
        } catch (erro) {
            if (erro.name !== "AbortError") {
                mensagem.textContent = erro.message;
            }
        }
    }

    entrada.addEventListener("input", atualizarQuartos);
    saida.addEventListener("input", atualizarQuartos);
    quarto.addEventListener("change", () => {
        quartoSelecionado = quarto.value;
        mostrarPrecoSelecionado();
    });
    atualizarQuartos();
}
