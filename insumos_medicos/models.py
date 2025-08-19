from django.db import models

class Inventario(models.Model):
    """
    Representa las ubicaciones del inventario (Principal, Cuartel, Estaciones 1, 2, 3, Enfermeria, Prehospitalaria).
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del inventario (ej: Principal, Estación 1)")
    is_principal = models.BooleanField(default=False, help_text="Marca si este es el inventario principal.")

    def __str__(self):
        return self.nombre
    
class TipoInsumo(models.Model):
    """
    Categorías para los insumos médicos.
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre de la categoría (ej: Material Quirúrgico)")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción de la categoría.")

    def __str__(self):
        return self.nombre
    
class Insumo(models.Model):
    """
    Representa un tipo de insumo médico genérico (ej: 'Pastillas de Paracetamol').
    """
    nombre = models.CharField(max_length=200, help_text="Nombre del insumo (ej: Cloruro de Sodio)")
    tipo = models.ForeignKey(TipoInsumo, on_delete=models.CASCADE, related_name='insumos', help_text="Tipo de insumo al que pertenece.")
    presentacion = models.CharField(max_length=100, help_text="Formato en que viene el insumo (ej: Caja x20, Frasco de 500ml)")
    descripcion = models.TextField(help_text="Descripción detallada del insumo.")

    def __str__(self):
        return f"{self.nombre} ({self.presentacion})"
    
class Lote(models.Model):
    """
    Representa un grupo de insumos que comparten la misma fecha de vencimiento.
    """
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='lotes', help_text="El tipo de insumo de este lote.")
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='lotes', help_text="El inventario donde se encuentra este lote.")
    cantidad = models.PositiveIntegerField(help_text="Número de items en el lote.")
    fecha_vencimiento = models.DateField(help_text="Fecha de vencimiento de los items en el lote.")
    fecha_ingreso = models.DateTimeField(auto_now_add=True, help_text="Fecha en que el lote fue registrado.")

    def __str__(self):
        return f"Lote de {self.insumo.nombre} - Cantidad: {self.cantidad} - Vence: {self.fecha_vencimiento}"
    
class Movimiento(models.Model):
    """
    Registra los movimientos de insumos para una trazabilidad completa.
    """
    TIPO_MOVIMIENTO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('ASIGNACION', 'Asignación'),
        ('DEVOLUCION', 'Devolución'),
    ]
    
    # Referencia al tipo de insumo (más estable que referenciar un lote)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos', help_text="El insumo que se movió.", default=None)
    # Campo para la fecha de vencimiento del lote original
    fecha_vencimiento_lote = models.DateField(help_text="Fecha de vencimiento del lote al momento del movimiento.", default=None)
    tipo_movimiento = models.CharField(max_length=15, choices=TIPO_MOVIMIENTO_CHOICES, help_text="Tipo de movimiento (Entrada, Salida, etc.).")
    cantidad = models.PositiveIntegerField(help_text="Cantidad de items que se movieron.")
    inventario_origen = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='movimientos_salida', help_text="Inventario desde donde se movió el insumo.")
    inventario_destino = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='movimientos_entrada', null=True, blank=True, help_text="Inventario al que se movió el insumo (opcional).")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora del movimiento.")
    descripcion = models.TextField(blank=True, null=True, help_text="Notas o detalles adicionales del movimiento.")

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} de {self.insumo.nombre}"