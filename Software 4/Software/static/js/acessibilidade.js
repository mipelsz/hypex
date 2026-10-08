let leituraVozAtiva =
    localStorage.getItem("leituraVoz") === "true";

function atualizarBotaoVoz() {

    if (!btnVoz || !iconeVoz) {
        return;
    }

    if (leituraVozAtiva) {

        iconeVoz.className = "bi bi-volume-up-fill";

        btnVoz.setAttribute(
            "aria-label",
            "Desativar leitura por voz"
        );

        btnVoz.setAttribute(
            "title",
            "Desativar leitura por voz"
        );

        btnVoz.setAttribute(
            "aria-pressed",
            "true"
        );

    } else {

        iconeVoz.className = "bi bi-volume-mute-fill";

        btnVoz.setAttribute(
            "aria-label",
            "Ativar leitura por voz"
        );

        btnVoz.setAttribute(
            "title",
            "Ativar leitura por voz"
        );

        btnVoz.setAttribute(
            "aria-pressed",
            "false"
        );

    }

}

function falar(texto) {

    if (!leituraVozAtiva) {
        return;
    }

    if (!("speechSynthesis" in window)) {
        return;
    }

    if (!texto || texto.trim() === "") {
        return;
    }

    window.speechSynthesis.cancel();

    const fala = new SpeechSynthesisUtterance(
        texto.trim()
    );

    fala.lang = "pt-BR";
    fala.rate = 1;
    fala.pitch = 1;
    fala.volume = 1;

    window.speechSynthesis.speak(fala);
}

if (btnVoz) {

    atualizarBotaoVoz();

    btnVoz.addEventListener("click", function () {

        leituraVozAtiva = !leituraVozAtiva;

        localStorage.setItem(
            "leituraVoz",
            leituraVozAtiva
        );

        atualizarBotaoVoz();

        if (leituraVozAtiva) {

            falar("Leitura por voz ativada.");

        } else {

            if ("speechSynthesis" in window) {
                window.speechSynthesis.cancel();
            }

        }

    });

}

document.addEventListener("focusin", function (event) {

    if (!leituraVozAtiva) {
        return;
    }

    const elemento = event.target;

    if (!elemento.matches(
        "a, button, input, select, textarea"
    )) {
        return;
    }

    let texto = elemento.getAttribute("aria-label");

    if (!texto) {
        texto = elemento.getAttribute("title");
    }

    if (!texto) {
        texto = elemento.innerText;
    }

    if (!texto) {
        texto = elemento.placeholder;
    }

    if (!texto || texto.trim() === "") {
        return;
    }

    falar(texto);

});

document.addEventListener("click", function (event) {

    if (!leituraVozAtiva) {
        return;
    }

    const elemento = event.target.closest("button");

    if (!elemento) {
        return;
    }

    if (elemento.id === "btnVoz") {
        return;
    }

    let texto = elemento.getAttribute("aria-label");

    if (!texto) {
        texto = elemento.getAttribute("title");
    }

    if (!texto) {
        texto = elemento.innerText;
    }

    if (!texto || texto.trim() === "") {
        return;
    }

    falar(texto);

});