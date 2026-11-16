
/* KOVA - Calendario anual de temporadas */
(function () {
    "use strict";

    const TEMPORADAS = {
        1: {
            nombre: "Año Nuevo",
            simbolos: ["✨", "⭐", "🎉"],
            mensaje: "¡Kova te desea un año lleno de alegría!",
            color: "#243b75"
        },
        2: {
            nombre: "Amor y Amistad",
            simbolos: ["❤️", "💕", "💗"],
            mensaje: "¡Kova te manda mucho cariño!",
            color: "#b83265"
        },
        3: {
            nombre: "Primavera",
            simbolos: ["🌸", "🌼", "🌷"],
            mensaje: "¡La primavera llegó a KOVA!",
            color: "#44894a"
        },
        4: {
            nombre: "Día del Niño",
            simbolos: ["🎈", "🎉", "⭐"],
            mensaje: "¡Que nunca falten los juegos y las sonrisas!",
            color: "#3978b8"
        },
        5: {
            nombre: "Día de las Madres",
            simbolos: ["🌷", "🌸", "❤️"],
            mensaje: "¡Kova celebra con cariño a todas las mamás!",
            color: "#a64775"
        },
        6: {
            nombre: "Verano",
            simbolos: ["☀️", "🌻", "✨"],
            mensaje: "¡Disfruta los días soleados con Kova!",
            color: "#bb7923"
        },
        7: {
            nombre: "Vacaciones",
            simbolos: ["☀️", "🏖️", "🌴"],
            mensaje: "¡Kova te desea unas vacaciones increíbles!",
            color: "#168b9b"
        },
        8: {
            nombre: "Regreso a Clases",
            simbolos: ["📚", "✏️", "⭐"],
            mensaje: "¡Un nuevo comienzo lleno de aprendizajes!",
            color: "#4266a3"
        },
        9: {
            nombre: "Mes Patrio",
            simbolos: ["🇲🇽", "💚", "🤍", "❤️"],
            mensaje: "¡Kova celebra con orgullo a México!",
            color: "#176846"
        },
        10: {
            nombre: "Halloween",
            simbolos: ["🎃", "👻", "🦇"],
            mensaje: "¡Kova te desea un Halloween divertido!",
            color: "#773d91"
        },
        11: {
            nombre: "Día de Muertos",
            simbolos: ["🏵️", "🧡", "🕯️", "🌼"],
            mensaje: "Recordamos con amor a quienes siempre vivirán en nuestro corazón. 🐾",
            color: "#69348a"
        },
        12: {
            nombre: "Navidad",
            simbolos: ["❄️", "❄️", "❄️"],
            mensaje: "¡Kova te desea felices fiestas!",
            color: "#185740",
            imagen: "/static/img/kova_navidad.webp"
        }
    };

    const CONFIG = {
        primeraAparicion: 3000,
        intervalo: 180000,
        duracion: 8000,
        cantidadDecoraciones: 22
    };

    const mes = new Date().getMonth() + 1;
    const temporada = TEMPORADAS[mes];

    let temporizador = null;
    let repeticion = null;
    let cerrado = false;

    function hayFormularioAbierto() {
        return [...document.querySelectorAll(
            ".modal, [role='dialog']"
        )].some(elemento => {
            const estilo = getComputedStyle(elemento);

            return estilo.display !== "none" &&
                estilo.visibility !== "hidden" &&
                elemento.getBoundingClientRect().height > 0;
        });
    }

    function ocultarSaludo() {
        const tarjeta = document.getElementById("kova-saludo");

        if (tarjeta) {
            tarjeta.classList.remove("visible");
        }
    }

    function mostrarSaludo() {
        if (cerrado || document.hidden || hayFormularioAbierto()) {
            return;
        }

        const tarjeta = document.getElementById("kova-saludo");

        if (!tarjeta) return;

        tarjeta.classList.add("visible");

        clearTimeout(temporizador);

        temporizador = setTimeout(
            ocultarSaludo,
            CONFIG.duracion
        );
    }

    function crearDecoracion() {
        const capa = document.createElement("div");

        capa.id = "kova-nieve";
        capa.className = "kova-decoracion";
        capa.setAttribute("aria-hidden", "true");

        for (let i = 0; i < CONFIG.cantidadDecoraciones; i++) {
            const elemento = document.createElement("span");

            elemento.textContent =
                temporada.simbolos[
                    i % temporada.simbolos.length
                ];

            elemento.style.left =
                (Math.random() * 100) + "%";

            elemento.style.fontSize =
                (15 + Math.random() * 12) + "px";

            elemento.style.animationDuration =
                (9 + Math.random() * 10) + "s";

            elemento.style.animationDelay =
                (-Math.random() * 18) + "s";

            capa.appendChild(elemento);
        }

        document.body.appendChild(capa);
    }

    function crearSaludo() {
        const tarjeta = document.createElement("div");

        tarjeta.id = "kova-saludo";
        tarjeta.setAttribute("role", "status");

        tarjeta.style.background =
            "linear-gradient(135deg, " +
            temporada.color +
            ", #242333)";

        const cerrar = document.createElement("button");
        cerrar.id = "kova-cerrar";
        cerrar.type = "button";
        cerrar.textContent = "×";
        cerrar.setAttribute("aria-label", "Cerrar saludo");

        cerrar.addEventListener("click", () => {
            cerrado = true;
            ocultarSaludo();
            clearInterval(repeticion);
        });

        tarjeta.appendChild(cerrar);

        if (temporada.imagen) {
            const imagen = document.createElement("img");

            imagen.src = temporada.imagen;
            imagen.alt = "Kova celebrando " + temporada.nombre;

            tarjeta.appendChild(imagen);
        } else {
            const mascota = document.createElement("div");

            mascota.className = "kova-icono-temporada";
            mascota.textContent = temporada.simbolos[0];

            tarjeta.appendChild(mascota);
        }

        const mensaje = document.createElement("div");
        mensaje.className = "kova-mensaje";

        const titulo = document.createElement("strong");
        titulo.textContent = "🐾 KOVA - " + temporada.nombre;

        const descripcion = document.createElement("span");
        descripcion.textContent = temporada.mensaje;

        mensaje.appendChild(titulo);
        mensaje.appendChild(descripcion);

        tarjeta.appendChild(mensaje);
        document.body.appendChild(tarjeta);
    }

    function iniciarTemporada() {
        if (!document.body || !temporada) return;

        // Evita crear elementos duplicados
        document.getElementById("kova-saludo")?.remove();
        document.getElementById("kova-nieve")?.remove();
        document.getElementById("kova-probar")?.remove();

        crearDecoracion();
        crearSaludo();

        setTimeout(
            mostrarSaludo,
            CONFIG.primeraAparicion
        );

        repeticion = setInterval(
            mostrarSaludo,
            CONFIG.intervalo
        );

        document.addEventListener("visibilitychange", () => {
            if (document.hidden) ocultarSaludo();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            iniciarTemporada,
            { once: true }
        );
    } else {
        iniciarTemporada();
    }
})();
