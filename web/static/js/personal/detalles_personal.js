
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleFormBtn');
    const formRow = document.getElementById('formRow');
    const cancelBtns = document.querySelectorAll('.cancel-form');
    
    toggleBtn.addEventListener('click', function() {
        if (formRow.style.display === 'none') {
            formRow.style.display = 'table-row';
            toggleBtn.textContent = 'Cancelar';
            toggleBtn.classList.remove('btn-danger');
            toggleBtn.classList.add('btn-secondary');
            formRow.querySelectorAll("input").forEach(e => e.setAttribute("required", true))
        } else {
            formRow.style.display = 'none';
            formRow.querySelectorAll("input").forEach(e => e.removeAttribute("required"))
            toggleBtn.textContent = 'Agregar Nuevo Ascenso';
            toggleBtn.classList.remove('btn-secondary');
            toggleBtn.classList.add('btn-danger');
        }
    });
    
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            formRow.style.display = 'none';
            formRow.querySelectorAll("input").forEach(e => e.removeAttribute("required"))
            toggleBtn.textContent = 'Agregar Nuevo Ascenso';
            toggleBtn.classList.remove('btn-secondary');
            toggleBtn.classList.add('btn-danger');
        });
    });
});