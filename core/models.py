from django.db import models
from django.contrib.auth.models import AbstractUser

#Modelo usuario con campos agregrados
class User(AbstractUser):
    class TipoDocumento(models.TextChoices):
        CEDULA = 'CC', 'Cédula de Ciudadanía / Identidad'
        PASAPORTE = 'PA', 'Pasaporte'
        RUC = 'RUC', 'Registro Único de Contribuyentes'
        DNI = 'DNI', 'Documento Nacional de Identidad'
        OTRO = 'OT', 'Otro'
    tipo_documento = models.CharField(
        max_length=255,
        choices=TipoDocumento.choices
        
    )
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    telefono = models.CharField(max_length=255,blank=True,null=True)
    no_documento = models.CharField(max_length=255,blank=True,null=True)
    nombres =models.CharField(max_length=255,blank=True,null=True,default='N')

#Modelo de cursos
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

#Modelo de modulos
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    class Meta:
        ordering = ['order']

#Leccciones
class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField() # O un campo FileField para videos/PDFs
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
#Progreso de estudiantes
class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'lesson')