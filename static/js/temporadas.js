
/* KOVA - Animación navideña */
(function () {
    "use strict";

    const CONFIG = {
        primeraAparicion: 15000,
        intervalo: 180000,
        duracion: 8000,
        imagen: "/static/img/kova_navidad.webp",
        mensaje: "🎄 ¡Kova te desea felices fiestas!"
    };

    const parametros = new URLSearchParams(window.location.search);
    const modoPrueba = parametros.get("kova_navidad") === "1";
    const mesActual = new Date().getMonth();

    // Navidad automática en diciembre o mediante modo prueba
    const navidadActiva = mesActual === 11 || modoPrueba;

    let temporizador = null;
    let repeticion = null;
    let oculto = false;

    function formularioAbierto() {
        return Array.from(
            document.querySelectorAll(".modal, [role='dialog']")
        ).some(elemento => {
            const estilo = getComputedStyle(elemento);
            return estilo.display !== "none" &&
                   estilo.visibility !== "hidden" &&
                   elemento.getBoundingClientRect().height > 0;
        });
    }

    function ocultarKova() {
        const saludo = document.getElementById("kova-saludo");
        if (saludo) saludo.classList.remove("visible");
    }

    function mostrarKova() {
        if (oculto || document.hidden || formularioAbierto()) return;

        const saludo = document.getElementById("kova-saludo");
        if (!saludo) return;

        saludo.classList.add("visible");

        clearTimeout(temporizador);
        temporizador = setTimeout(ocultarKova, CONFIG.duracion);
    }

    function crearNieve() {
        const capa = document.createElement("div");
        capa.id = "kova-nieve";
        capa.setAttribute("aria-hidden", "true");

        for (let i = 0; i < 25; i++) {
            const copo = document.createElement("span");
            copo.textContent = "❄";
            copo.style.left = Math.random() * 100 + "%";
            copo.style.fontSize = (10 + Math.random() * 12) + "px";
            copo.style.animationDuration =
                (8 + Math.random() * 10) + "s";
            copo.style.animationDelay =
                (-Math.random() * 18) + "s";
            capa.appendChild(copo);
        }

        document.body.appendChild(capa);
    }

    function iniciarKova() {
        // Eliminar versiones anteriores si existen
        document.getElementById("kova-saludo")?.remove();
        document.getElementById("kova-nieve")?.remove();
        document.getElementById("kova-probar")?.remove();

        if (!navidadActiva) return;

        crearNieve();

        const saludo = document.createElement("div");
        saludo.id = "kova-saludo";
        saludo.setAttribute("role", "status");

        saludo.innerHTML = `
            <button id="kova-cerrar" type="button"
                    aria-label="Cerrar saludo">×</button>
            <img src="${CONFIG.imagen}"
                 alt="Kova saludando con traje navideño">
            <div class="kova-mensaje">
                <strong>¡Hola! Soy Kova 🐾</strong>
                <span>${CONFIG.mensaje}</span>
            </div>
        `;

        document.body.appendChild(saludo);

        document.getElementById("kova-cerrar")
            .addEventListener("click", () => {
                oculto = true;
                ocultarKova();
                clearInterval(repeticion);
            });

        // Botón para probar el saludo inmediatamente
        const probar = document.createElement("button");
        probar.id = "kova-probar";
        probar.type = "button";
        probar.textContent = "🐾 Saludar con Kova";

        probar.addEventListener("click", () => {
            oculto = false;
            mostrarKova();
        });

        document.body.appendChild(probar);

        // Primera aparición
        setTimeout(mostrarKova, CONFIG.primeraAparicion);

        // Apariciones posteriores
        repeticion = setInterval(
            mostrarKova,
            CONFIG.intervalo
        );

        // Ocultar si el usuario cambia de pestaña
        document.addEventListener("visibilitychange", () => {
            if (document.hidden) ocultarKova();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            iniciarKova
        );
    } else {
        iniciarKova();
    }
})();
