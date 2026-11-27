from import_export import resources
from .models import User,UserToken,UserSession,School,Instructor,Course,CourseInstructor,CourseEdition,CourseModule,Lesson,LessonResource,LiveSession,Company,CompanyMember,CompanyProgram,CompanyProgramCourse,Coupon,Order,OrderItem,Payment,Enrollment,LessonProgress,SessionAttendance,Assessment,Question,QuestionOption,QuestionAnswerKey,Attempt,AttemptAnswer,Certificate,Testimonial,ContactLead,SalesByMonth,CourseStats,CompanyReport

class UserResource(resources.ModelResource):
    class Meta:
        model = User        
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class UserTokenResource(resources.ModelResource):
    class Meta:
        model = UserToken
        import_id_fields = ('id',)  # Field used to identify existing records during import        
        report_skipped = False

class UserSessionResource(resources.ModelResource):
    class Meta:
        model = UserSession
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class SchoolResource(resources.ModelResource):
    class Meta:
        model = School
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class InstructorResource(resources.ModelResource):
    class Meta:
        model = Instructor
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CourseResource(resources.ModelResource):
    class Meta:
        model = Course
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CourseInstructorResource(resources.ModelResource):
    class Meta:
        model = CourseInstructor
        import_id_fields = ("course", "instructor",)
        skip_unchanged = True
        report_skipped = False

class CourseEditionResource(resources.ModelResource):
    class Meta:
        model = CourseEdition
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CourseModuleResource(resources.ModelResource):
    class Meta:
        model = CourseModule
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class LessonImportResource(resources.ModelResource):
    class Meta:
        model = Lesson
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
class LessonResourceResource(resources.ModelResource):
    class Meta:
        model = LessonResource   # el modelo, ya sin colisión
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False

class LiveSessionResource(resources.ModelResource):
    class Meta:
        model = LiveSession
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False


class CompanyMemberResource(resources.ModelResource):
    class Meta:
        model = CompanyMember
        import_id_fields = ("company", "user",)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CompanyProgramResource(resources.ModelResource):
    class Meta:
        model = CompanyProgram
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CompanyProgramCourseResource(resources.ModelResource):
    class Meta:
        model = CompanyProgramCourse
        import_id_fields = ("program", "course",)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False
class CouponResource(resources.ModelResource):
    class Meta:
        model = Coupon
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False

class OrderItemResource(resources.ModelResource):
    class Meta:
        model = OrderItem
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class PaymentResource(resources.ModelResource):
    class Meta:
        model = Payment
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class EnrollmentResource(resources.ModelResource):
    class Meta:
        model = Enrollment
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class LessonProgressResource(resources.ModelResource):
    class Meta:
        model = LessonProgress
        import_id_fields = ("enrollment", "lesson")  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class SessionAttendanceResource(resources.ModelResource):
    class Meta:
        model = SessionAttendance
        import_id_fields = ("session", "enrollment",)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class AssessmentResource(resources.ModelResource):
    class Meta:
        model = Assessment
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class QuestionOptionResource(resources.ModelResource):
    class Meta:
        model = QuestionOption
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class QuestionAnswerKeyResource(resources.ModelResource):
    class Meta:
        model = QuestionAnswerKey
        import_id_fields = ("question", "option",)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class AttemptResource(resources.ModelResource):
    class Meta:
        model = Attempt
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False


class AttemptAnswerResource(resources.ModelResource):
    class Meta:
        model = AttemptAnswer
        import_id_fields = ("attempt", "question",)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CertificateResource(resources.ModelResource):
    class Meta:
        model = Certificate
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class TestimonialResource(resources.ModelResource):
    class Meta:
        model = Testimonial
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False


class ContactLeadResource(resources.ModelResource):
    class Meta:
        model = ContactLead
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class SalesByMonthResource(resources.ModelResource):
    class Meta:
        model = SalesByMonth
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CourseStatsResource(resources.ModelResource):
    class Meta:
        model = CourseStats
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False

class CompanyReportResource(resources.ModelResource):
    class Meta:
        model = CompanyReport
        import_id_fields = ('id',)  # Field used to identify existing records during import
        skip_unchanged = True
        report_skipped = False