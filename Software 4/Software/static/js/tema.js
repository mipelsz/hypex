(function () {

    function salvar(form, extra) {
        var dados = new FormData(form);
        if (extra) {
            dados.append(extra.name, extra.value);
        }
        fetch(form.action, { method: "POST", body: dados, redirect: "manual" })
            .catch(function () {});
    }

    var formTema = document.querySelector(".tema-toggle");

    if (formTema) {
        formTema.addEventListener("submit", function (evento) {
            evento.preventDefault();

            var botao = evento.submitter;
            if (!botao) {
                return;
            }

            var escuro = botao.value === "escuro";
            var body = document.body;

            if (body.classList.contains("modo-escuro") === escuro) {
                return;
            }

            body.classList.add("trocando-tema");
            body.classList.toggle("modo-escuro", escuro);
            setTimeout(function () {
                body.classList.remove("trocando-tema");
            }, 400);

            formTema.querySelectorAll("button[name=tema]").forEach(function (b) {
                var ativo = b.value === (escuro ? "escuro" : "claro");
                b.classList.toggle("ativo", ativo);
                b.setAttribute("aria-pressed", ativo ? "true" : "false");
            });

            salvar(formTema, botao);
        });
    }

    var formMenu = document.getElementById("form-menu");
    var menu = document.getElementById("menu");

    if (formMenu && menu) {
        formMenu.addEventListener("submit", function (evento) {
            evento.preventDefault();

            var minimizada = !menu.classList.contains("minimizada");
            menu.classList.toggle("minimizada", minimizada);
            document.body.classList.toggle("sidebar-minimizada", minimizada);

            var botao = document.getElementById("btn-minimizar");
            if (botao) {
                botao.title = minimizada ? "Expandir menu" : "Minimizar menu";
            }

            salvar(formMenu);
        });
    }

})();
