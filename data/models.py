from django.db import models

class Cliente(models.Model):
    ci = models.CharField(max_length=11, unique=True)
    nombre = models.CharField(max_length=300)
    primer_apellido = models.CharField(max_length=300)
    segundo_apellido = models.CharField(max_length=300)
    tipo_entrenamiento = models.CharField(max_length=300, default='Normal')
    numero_de_telefono = models.CharField(max_length=300, default='')
    notificado = models.BooleanField(default=False)
    fecha_ingreso = models.DateField(auto_now_add=True)
    ultimo_pago = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to=f'images/')

    def nombre_completo(self):
        return f'{self.nombre} {self.primer_apellido} {self.segundo_apellido}'

    def get_dict(self):
        return {
            "ci": self.ci,
            "nombre": self.nombre,
            "primer_apellido": self.primer_apellido,
            "segundo_apellido": self.segundo_apellido,
            "tipo_entrenamiento": self.tipo_entrenamiento,
            "fecha_ingreso": self.fecha_ingreso,
            "ultimo_pago": self.ultimo_pago,
            "foto": self.foto
        }