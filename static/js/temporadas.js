
/* KOVA - Sistema automático de temporadas */
(() => {
    "use strict";

    if (window.__kovaTemporadasIniciado) return;
    window.__kovaTemporadasIniciado = true;

    const BASE = "/static/img/";

    const CALENDARIO = {
        1:  { nombre: "Año Nuevo", emoji: ["✨", "⭐"], mensaje: "¡Un nuevo año de aventuras!", color: "#263f83" },
        2:  { nombre: "Amor y Amistad", emoji: ["💕", "❤️"], mensaje: "¡Mucho cariño de parte de Kova!", color: "#a72e68" },
        3:  { nombre: "Primavera", emoji: ["🌸", "🌷"], mensaje: "¡Bienvenida la primavera!", color: "#448b54" },
        4:  { nombre: "Día del Niño", emoji: ["🎈", "⭐"], mensaje: "¡A jugar y disfrutar!", color: "#287ca3" },
        5:  { nombre: "Día de las Madres", emoji: ["🌷", "💗"], mensaje: "¡Con cariño para todas las mamás!", color: "#a94c7a" },
        6:  { nombre: "Verano", emoji: ["☀️", "🌻"], mensaje: "¡Disfruta los días soleados!", color: "#b87822" },
        7:  { nombre: "Vacaciones", emoji: ["🌴", "☀️"], mensaje: "¡Felices vacaciones!", color: "#168b9b" },
        8:  { nombre: "Regreso a Clases", emoji: ["📚", "✏️"], mensaje: "¡Mucho éxito en este nuevo comienzo!", color: "#4866a4" },
        9:  { nombre: "Mes Patrio", emoji: ["🇲🇽", "💚"], mensaje: "¡Viva México!", color: "#176b48" },
        10: { nombre: "Halloween", emoji: ["🎃", "👻"], mensaje: "¡Una celebración espeluznante!", color: "#793c92" },
        11: {
            nombre: "Día de Muertos",
            emoji: ["🏵️", "🌼"],
            mensaje: "Recordamos con amor a quienes siempre vivirán en nuestro corazón.",
            color: "#71308b",
            imagen: BASE + "kova_dia_muertos.gif"
        },
        12: {
            nombre: "Navidad",
            emoji: ["❄️", "⭐"],
            mensaje: "¡Kova te desea felices fiestas!",
            color: "#16583d",
            imagen: BASE + "kova_navidad_3d.gif"
        }
    };

    const config = {
        primeraAparicion: 3000,
        cadaCuanto: 180000,
        duracion: 9000,
        cantidad: 16
    };

    let tarjeta, tiempoOcultar;
    let cerrada = false;

    function obtenerTemporada() {
        return CALENDARIO[new Date().getMonth() + 1];
    }

    function modalAbierto() {
        return [...document.querySelectorAll(
            ".modal, [role='dialog'], dialog[open]"
        )].some(el => {
            const estilo = getComputedStyle(el);
            return estilo.display !== "none" &&
                   estilo.visibility !== "hidden" &&
                   el.getBoundingClientRect().height > 0;
        });
    }

    function ocultar() {
        if (tarjeta) tarjeta.classList.remove("kova-visible");
    }

    function mostrar() {
        if (cerrada || document.hidden || modalAbierto()) return;
        if (!tarjeta) return;

        tarjeta.classList.add("kova-visible");
        clearTimeout(tiempoOcultar);
        tiempoOcultar = setTimeout(ocultar, config.duracion);
    }

    function crearTarjeta(temporada) {
        tarjeta = document.createElement("aside");
        tarjeta.id = "kova-tarjeta-temporada";
        tarjeta.style.setProperty("--kova-color", temporada.color);
        tarjeta.setAttribute("aria-label", "Saludo de temporada");

        const cerrar = document.createElement("button");
        cerrar.type = "button";
        cerrar.className = "kova-cerrar-temporada";
        cerrar.textContent = "×";
        cerrar.setAttribute("aria-label", "Cerrar saludo");
        cerrar.addEventListener("click", () => {
            cerrada = true;
            ocultar();
        });

        const visual = document.createElement(
            temporada.imagen ? "img" : "div"
        );
        visual.className = "kova-visual-temporada";

        if (temporada.imagen) {
            visual.src = temporada.imagen;
            visual.alt = "Kova celebrando " + temporada.nombre;
            visual.loading = "eager";
        } else {
            visual.textContent = temporada.emoji[0];
        }

        const titulo = document.createElement("strong");
        titulo.textContent = "🐾 KOVA - " + temporada.nombre;

        const mensaje = document.createElement("p");
        mensaje.textContent = temporada.mensaje;

        tarjeta.append(cerrar, visual, titulo, mensaje);
        document.body.appendChild(tarjeta);
    }

    function crearDecoraciones(temporada) {
        const capa = document.createElement("div");
        capa.id = "kova-capa-temporada";
        capa.setAttribute("aria-hidden", "true");

        for (let i = 0; i < config.cantidad; i++) {
            const figura = document.createElement("span");
            figura.textContent =
                temporada.emoji[i % temporada.emoji.length];
            figura.style.left = (Math.random() * 100) + "%";
            figura.style.fontSize = (13 + Math.random() * 12) + "px";
            figura.style.animationDuration =
                (9 + Math.random() * 9) + "s";
            figura.style.animationDelay =
                (-Math.random() * 18) + "s";
            capa.appendChild(figura);
        }

        document.body.appendChild(capa);
    }

    function iniciar() {
        if (!document.body) return;

        const temporada = obtenerTemporada();

        // Limpiar decoraciones de implementaciones anteriores
        [
            "kova-saludo",
            "kova-nieve",
            "kova-probar",
            "kova-dia-muertos",
            "kova-tarjeta-temporada",
            "kova-capa-temporada"
        ].forEach(id => document.getElementById(id)?.remove());

        crearDecoraciones(temporada);
        crearTarjeta(temporada);

        setTimeout(mostrar, config.primeraAparicion);
        setInterval(mostrar, config.cadaCuanto);

        document.addEventListener("visibilitychange", () => {
            if (document.hidden) ocultar();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    } else {
        iniciar();
    }
})();
