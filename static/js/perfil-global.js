
/* KOVA - Acceso global al perfil */
(function () {
    'use strict';

    function iniciarPerfilGlobal() {
        // Evitar botones duplicados
        if (document.querySelector('.kova-profile-link')) {
            return;
        }

        // Solo mostrarlo si Flask reconoce la sesión
        fetch('/api/perfil', {
            credentials: 'same-origin',
            cache: 'no-store'
        })
        .then(response => {
            if (!response.ok) return null;
            return response.json();
        })
        .then(datos => {
            if (!datos || !datos.success) return;

            const encabezado = document.querySelector(
                'header.topbar, header.navbar'
            );

            if (!encabezado) return;

            const enlace = document.createElement('a');
            enlace.href = '/perfil';
            enlace.className = 'kova-profile-link';
            enlace.setAttribute('aria-label', 'Mi perfil');

            const icono = document.createElement('span');
            icono.textContent = '👤';
            icono.setAttribute('aria-hidden', 'true');

            const texto = document.createElement('span');
            texto.className = 'kova-profile-label';
            texto.textContent = 'Mi perfil';

            enlace.append(icono, texto);

            // Si existe un contenedor de acciones,
            // integrar el enlace en él.
            const contenedor = encabezado.querySelector(
                '.header-actions, .topbar-actions, .nav-actions'
            );

            if (contenedor) {
                contenedor.appendChild(enlace);
            } else {
                // Si no existe, agregarlo al final del header.
                const navegacion = document.createElement('div');
                navegacion.className = 'kova-profile-nav';
                navegacion.appendChild(enlace);
                encabezado.appendChild(navegacion);
            }
        })
        .catch(error => {
            console.warn('Perfil KOVA no disponible:', error);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener(
            'DOMContentLoaded',
            iniciarPerfilGlobal
        );
    } else {
        iniciarPerfilGlobal();
    }
})();
