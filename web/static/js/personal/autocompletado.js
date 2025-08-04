document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('institucion-autocomplete');
    const resultsContainer = document.getElementById('autocomplete-results');
    const hiddenInput = document.getElementById('{{ detalles.form_titulos.institucion.id_for_label }}');
    let instituciones = []; // Almacenará todos los datos

    // 1. Carga inicial de todas las instituciones
    fetch('/buscar_instituciones/?q=')
      .then(response => response.json())
      .then(data => {
        instituciones = data;
      });

    // 2. Búsqueda local con debounce
    let timeout;
    input.addEventListener('input', function(e) {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        const query = e.target.value.toLowerCase().trim();
        resultsContainer.innerHTML = '';
        
        if (query.length === 0) {
          resultsContainer.style.display = 'none';
          return;
        }

        const filtered = instituciones.filter(item => 
          item.nombre.toLowerCase().includes(query)
        );

        if (filtered.length > 0) {
          filtered.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.textContent = item.nombre;
            div.dataset.id = item.id;
            
            div.addEventListener('click', function() {
              input.value = item.nombre;
              if (hiddenInput) hiddenInput.value = item.id;
              resultsContainer.style.display = 'none';
            });
            
            resultsContainer.appendChild(div);
          });
          resultsContainer.style.display = 'block';
        } else {
          resultsContainer.style.display = 'none';
        }
      }, 300); // Debounce de 300ms
    });

    // Cerrar al hacer clic fuera
    document.addEventListener('click', function(e) {
      if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.style.display = 'none';
      }
    });
  });