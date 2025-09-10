document.addEventListener('DOMContentLoaded', function(){
    openTab('general');
});

function openTab(tab){
    document.querySelectorAll('.tab-content').forEach(elem => elem.style.display = 'none');
    document.getElementById(`${tab}-content`).style.display = 'block';

    document.querySelectorAll('.tab-button').forEach(elem => elem.classList.remove('active'));
    document.getElementById(`${tab}-button`).classList.add('active');
}