document.addEventListener('DOMContentLoaded', () => {
    let buttons = document.querySelectorAll('.order-actions-button');
    let dropdowns = document.querySelectorAll('.order-actions-dropdown');

    dropdowns.forEach(dropdown => {
        dropdown.style.display = 'none';
    });

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            let link = button.nextElementSibling;

            dropdowns.forEach(dropdown => {
                if (dropdown === link){
                    if (dropdown.style.display === 'none'){
                        dropdown.style.display = 'flex';
                    } else {
                        dropdown.style.display = 'none';
                    }
                } else {
                    dropdown.style.display = 'none';
                }
            });
        });
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.order-actions-button') && !event.target.closest('order-actions-dropdown')){
            dropdowns.forEach(dropdown => {
                dropdown.style.display = 'none';
            });
        } 
    });
});