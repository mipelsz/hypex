document.addEventListener("DOMContentLoaded", function () {

    var selectProduto = document.getElementById("select-produto");

    if (!selectProduto) {
        return;
    }

    var selectGalpao     = document.getElementById("select-galpao");
    var selectFornecedor = document.getElementById("select-fornecedor");
    var campoPreco       = document.getElementById("campo-preco");
    var campoQuantidade  = document.getElementById("campo-quantidade");

    var galpaoDoPedido     = document.getElementById("galpao-do-pedido");
    var fornecedorDoPedido = document.getElementById("fornecedor-do-pedido");
    var todasAsOpcoes = [];

    Array.prototype.forEach.call(selectProduto.options, function (opcao) {
        if (opcao.value) {
            todasAsOpcoes.push(opcao);
        }
    });

    var textoInicial = selectProduto.options.length
        ? selectProduto.options[0].textContent
        : "-- Selecione o produto --";

    function filtrarProdutos() {

        var filtroGalpao = selectGalpao ? selectGalpao.value : "";
        var filtroFornecedor = selectFornecedor ? selectFornecedor.value : "";
        var chaveAtiva = selectFornecedor ? filtroFornecedor : filtroGalpao;

        var selecionadoAntes = selectProduto.value;
        var disponiveis = [];

        todasAsOpcoes.forEach(function (opcao) {
            var serve;

            if (selectFornecedor) {
                var doFornecedor = opcao.getAttribute("data-fornecedor") || "";
                serve = !filtroFornecedor
                    || doFornecedor === ""
                    || doFornecedor === filtroFornecedor;
            } else {
                serve = opcao.getAttribute("data-galpao") === filtroGalpao;
            }

            if (serve) {
                disponiveis.push(opcao);
            }
        });

        selectProduto.innerHTML = "";

        var vazia = document.createElement("option");
        vazia.value = "";

        if (!chaveAtiva) {
            vazia.textContent = textoInicial;
        } else if (!disponiveis.length) {
            vazia.textContent = selectFornecedor
                ? "-- Nenhum produto para este fornecedor --"
                : "-- Nenhum produto com saldo neste galpão --";
        } else {
            vazia.textContent = "-- Selecione o produto --";
        }

        selectProduto.appendChild(vazia);

        disponiveis.forEach(function (opcao) {
            selectProduto.appendChild(opcao);
        });

        if (selecionadoAntes) {
            selectProduto.value = selecionadoAntes;
        }

        selectProduto.disabled = !chaveAtiva || !disponiveis.length;

        if (galpaoDoPedido && selectGalpao) {
            galpaoDoPedido.value = selectGalpao.value;
        }

        if (fornecedorDoPedido && selectFornecedor) {
            fornecedorDoPedido.value = selectFornecedor.value;
        }

        preencherPreco();
    }

    function preencherPreco() {

        var opcao = selectProduto.options[selectProduto.selectedIndex];

        if (!selectProduto.value || !opcao) {
            if (campoPreco) {
                campoPreco.value = "";
            }
            return;
        }

        var preco = opcao.getAttribute("data-preco");
        var saldo = opcao.getAttribute("data-saldo");

        if (campoPreco && preco !== null) {
            campoPreco.value = campoPreco.readOnly
                ? parseFloat(preco).toFixed(2).replace(".", ",")
                : parseFloat(preco).toFixed(2);
        }

        if (campoQuantidade && saldo !== null) {
            campoQuantidade.max = saldo;

            if (parseFloat(campoQuantidade.value) > parseFloat(saldo)) {
                campoQuantidade.value = saldo;
            }
        }
    }

    if (selectGalpao) {
        selectGalpao.addEventListener("change", filtrarProdutos);
    }

    if (selectFornecedor) {
        selectFornecedor.addEventListener("change", filtrarProdutos);
    }

    selectProduto.addEventListener("change", preencherPreco);

    filtrarProdutos();
});
