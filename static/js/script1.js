// Funcionalidad de las Tarjetas (Expandir Info al dar clic)
function mostrarInfo(idCard) {
    // Busca el div de información extra dentro de la tarjeta clicada
    let info = document.getElementById('info-' + idCard);
    
    // Alterna entre mostrar y ocultar
    if (info.style.display === "block") {
        info.style.display = "none";
    } else {
        info.style.display = "block";
    }
}

// Lógica del Carrusel de Sofía
let slideIndex = 1;
mostrarSlides(slideIndex);

function cambiarSlide(n) {
    mostrarSlides(slideIndex += n);
}

function mostrarSlides(n) {
    let i;
    let slides = document.getElementsByClassName("carousel-slide");
    
    if (n > slides.length) { slideIndex = 1 }    
    if (n < 1) { slideIndex = slides.length }
    
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";  
    }
    
    // Solo muestra la imagen actual si existen elementos
    if (slides.length > 0) {
        slides[slideIndex-1].style.display = "block";  
    }
}