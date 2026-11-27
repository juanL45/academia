from rest_framework import permissions
from .models import CompanyMember, CompanyRole
from rest_framework.permissions import BasePermission
from django.db import models
from django.utils import timezone
from .models import Enrollment, EnrollmentStatus, CourseInstructor, UserRole, Course
class IsCompanyMember(permissions.BasePermission):
  """Permite el acceso solo si el usuario autenticado pertenece a la empresa."""

  def has_permission(self, request, view):
    if not request.user or not request.user.is_authenticated:
      return False
    company_id = view.kwargs.get("company_id")
    return CompanyMember.objects.filter(
        company_id=company_id, user=request.user
    ).exists()


class IsCompanyAdminOrReadOnly(IsCompanyMember):
  """Lectura para cualquier miembro; escritura solo para administradores."""

  def has_permission(self, request, view):
    if not super().has_permission(request, view):
      return False
    if request.method in permissions.SAFE_METHODS:
      return True

    company_id = view.kwargs.get("company_id")
    # Ajusta 'ADMIN' según los valores reales de tu enum CompanyRole
    return CompanyMember.objects.filter(
        company_id=company_id,
        user=request.user,
        role=CompanyRole.ADMIN,
    ).exists()

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permite el acceso únicamente a administradores o docentes.
    Bloquea estrictamente a los alumnos.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Ajusta esta condición según tu modelo de usuario (ej. user.role == 'teacher' o grupos)
        return user.is_staff or getattr(user, "role", None) in ("teacher", "admin","instructor","student")


def has_course_access(user, course) -> bool:
    if not user.is_authenticated:
        return False
    if user.role == UserRole.ADMIN and user.is_active:
        return True
    now = timezone.now()
    if Enrollment.objects.filter(
        user=user,
        course=course,
        status__in=[EnrollmentStatus.ACTIVA, EnrollmentStatus.COMPLETADA],
    ).filter(models.Q(access_until__isnull=True) | models.Q(access_until__gt=now)).exists():
        return True
    return CourseInstructor.objects.filter(course=course, instructor__user=user).exists()


class HasCourseAccessPermission(permissions.BasePermission):
    message = "No tienes acceso activo a este curso."

    def has_permission(self, request, view):
        # Valida que el token JWT corresponda a un usuario autenticado
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Si el objeto es directamente un Course, lo pasa; si es una Lección/Módulo, extrae obj.course
        course = obj if isinstance(obj, Course) else getattr(obj, "course", None)
        if course is None:
            return False
        return has_course_access(request.user, course)