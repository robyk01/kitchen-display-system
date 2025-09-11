document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash-message').forEach(elem => {
        setTimeout( () => {
            elem.classList.add('fade-out');
            flash.addEventListener("animationend", () => {
                flash.remove();
            });
        }, 1500);
    });
});