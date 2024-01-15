from django.db import models
from datetime import timedelta, date

class Cliente(models.Model):
    ci = models.CharField(max_length=11, unique=True)
    nombre = models.CharField(max_length=300)
    primer_apellido = models.CharField(max_length=300)
    segundo_apellido = models.CharField(max_length=300)
    tipo_entrenamiento = models.CharField(max_length=300, default='Normal')
    numero_de_telefono = models.CharField(max_length=300, default='')
    deudor = models.BooleanField(default=False)
    notificado = models.BooleanField(default=False)
    debe_notificarse = models.BooleanField(default=False)
    fecha_ingreso = models.DateField()
    ultimo_pago = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to=f'images/')


    def nombre_completo(self):
        return f'{self.nombre} {self.primer_apellido} {self.segundo_apellido}'
    
    def get_date_30_days_after_ultimo_pago(self):
        date_30_days_after_ultimo_pago = self.ultimo_pago + timedelta(days=30)
        today = date.today()
        if today >= date_30_days_after_ultimo_pago - timedelta(days=5) and today < date_30_days_after_ultimo_pago:
            self.debe_notificarse = True
        elif today >= date_30_days_after_ultimo_pago:
            self.debe_notificarse = True
            self.deudor = True

        self.save()


    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the object is new
            if self.fecha_ingreso is None:
                self.fecha_ingreso = date.today()
                self.ultimo_pago = self.fecha_ingreso
        super().save(*args, **kwargs)  # Call the "real" save() method


    def get_dict(self):
        return {
            "ci": self.ci,
            "nombre": self.nombre,
            "primer_apellido": self.primer_apellido,
            "segundo_apellido": self.segundo_apellido,
            "tipo_entrenamiento": self.tipo_entrenamiento,
            "fecha_ingreso": self.fecha_ingreso,
            "ultimo_pago": self.ultimo_pago,
            "deudor": self.deudor,
            "notificado": self.notificado,
            "debe_notificarse": self.debe_notificarse,
            "numero_de_telefono": self.numero_de_telefono,
            "foto": self.foto
        }

