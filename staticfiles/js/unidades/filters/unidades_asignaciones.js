// Script para múltiples filtros
document.addEventListener('DOMContentLoaded', function() {
    const filterHerramienta = document.querySelector('.filter-herramienta');
    const filterResponsable = document.querySelector('.filter-responsable');
    const tableRows = document.querySelectorAll('.div-responsive-table tbody tr');
  
    function aplicarFiltros() {
      const termHerramienta = filterHerramienta.value.toLowerCase();
      const termResponsable = filterResponsable.value.toLowerCase();
  
      tableRows.forEach(row => {
        const herramientaText = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
        const responsableText = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
        
        const visibleHerramienta = herramientaText.includes(termHerramienta);
        const visibleResponsable = responsableText.includes(termResponsable);
        
        // Mostrar solo si coincide con AMBOS filtros (AND lógico)
        row.style.display = (visibleHerramienta && visibleResponsable) ? '' : 'none';
        
        // Resaltados independientes
        row.querySelector('td:nth-child(1)').style.backgroundColor = 
          termHerramienta && visibleHerramienta ? 'yellow' : '';
        
        row.querySelector('td:nth-child(4)').style.backgroundColor = 
          termResponsable && visibleResponsable ? 'yellow' : '';
      });
    }
  
    filterHerramienta.addEventListener('input', aplicarFiltros);
    filterResponsable.addEventListener('input', aplicarFiltros);
  });