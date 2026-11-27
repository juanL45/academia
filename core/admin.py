from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportMixin

from .models import (
    User, UserToken, UserSession, School, Instructor, Course, CourseEdition,
    CourseModule, Lesson, LessonResource, LiveSession, Company, CompanyProgram,
    Coupon, Order, OrderItem, Payment, Enrollment, Assessment, Question,
    QuestionOption, Attempt, Certificate, Testimonial, ContactLead,
    SalesByMonth, CourseStats,
)
from . import resources as r


def register(model, resource, base=ImportExportModelAdmin):
    admin_cls = type(f"{model.__name__}Admin", (base,), {"resource_classes": [resource]})
    admin.site.register(model, admin_cls)


class ReadOnlyExportAdmin(ExportMixin, admin.ModelAdmin):
    """Para vistas de reportes: solo exportar, sin crear/editar/borrar."""
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


register(User, r.UserResource)
register(UserToken, r.UserTokenResource)
register(UserSession, r.UserSessionResource)
register(School, r.SchoolResource)
register(Instructor, r.InstructorResource)
register(Course, r.CourseResource)
register(CourseEdition, r.CourseEditionResource)
register(CourseModule, r.CourseModuleResource)
register(Lesson, r.LessonImportResource)            # corregido
register(LessonResource, r.LessonResourceResource)  # faltaba registrarlo
register(LiveSession, r.LiveSessionResource)
register(Company, r.CompanyResource)
register(CompanyProgram, r.CompanyProgramResource)
register(Coupon, r.CouponResource)
register(Order, r.OrderResource)
register(OrderItem, r.OrderItemResource)
register(Payment, r.PaymentResource)
register(Enrollment, r.EnrollmentResource)
register(Assessment, r.AssessmentResource)
register(Question, r.QuestionResource)
register(QuestionOption, r.QuestionOptionResource)
register(Attempt, r.AttemptResource)
register(Certificate, r.CertificateResource)
register(Testimonial, r.TestimonialResource)
register(ContactLead, r.ContactLeadResource)

# Vistas de solo lectura
register(SalesByMonth, r.SalesByMonthResource, base=ReadOnlyExportAdmin)
register(CourseStats, r.CourseStatsResource, base=ReadOnlyExportAdmin)