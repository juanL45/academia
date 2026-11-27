from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    
)

from django.contrib import admin
from django.urls import include, path
from core import views
from rest_framework.routers import DefaultRouter

from core.views import (
    LoginControllerView,
    LogoutControllerView,
    ProfileControllerView,
    RegisterControllerView,
    CrearPagoView,
    SchoolViewSet,
    InstructorViewSet,
    CourseViewSet,
    CourseInstructorDetailAPIView,
    CourseInstructorListCreateAPIView,
    CourseEditionViewSet,
    LessonViewSet,
    CourseModuleViewSet,
    LessonResourceViewSet,
    LiveSessionDetailView,
    LiveSessionListCreateView,
    LiveSessionRecordingUpdateView,
    CompanyViewSet,
    CompanyMemberViewSet,
    CompanyProgramViewSet,
    CompanyProgramCourseViewSet,
    CouponViewSet,
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
    EnrollmentViewSet,

    LessonProgressDetailView,
    LessonProgressListView,
    LessonProgressUpsertView,

    SessionAttendanceListCreateView,
    SessionAttendanceDetailView,
    QuestionViewSet,
    QuestionOptionViewSet,
    QuestionAnswerKeyListCreateView, 
    QuestionAnswerKeyDeleteView,

    AttemptAnswerListUpsertView, AttemptAnswerDetailView,

    CertificateViewSet, VerifyCertificateAPIView, TestimonialViewSet,ContactLeadViewSet,
    CompanyReportViewSet,
    CourseStatsViewSet,
    SalesByMonthViewSet,

     CourseClassroomView,

     AttemptViewSet,
     AssessmentViewSet
)

router = DefaultRouter()
router.register(r"schools", SchoolViewSet, basename="school")
router.register(r"instructors", InstructorViewSet, basename="instructor")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"course-editions", CourseEditionViewSet, basename="course-edition")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r'modules', CourseModuleViewSet, basename='course-module')
router.register(r"lesson-resources", LessonResourceViewSet, basename="lesson-resource")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"company-programs", CompanyProgramViewSet, basename="company-program")
router.register(r"coupons", CouponViewSet, basename="coupon")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items", OrderItemViewSet, basename="order-item")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"question-options", QuestionOptionViewSet, basename="question-option")
router.register(r"certificates", CertificateViewSet, basename="certificate")
router.register(r"testimonials", TestimonialViewSet, basename="testimonial")
router.register(r"contact-leads", ContactLeadViewSet, basename="contact-lead")
router.register(r"reports/sales-by-month", SalesByMonthViewSet, basename="sales-by-month")
router.register(r"reports/course-stats", CourseStatsViewSet, basename="course-stats")
router.register(r"attempts", AttemptViewSet, basename="attempt")
router.register(r"assesments", AssessmentViewSet, basename="assesment")
member_list = CompanyMemberViewSet.as_view({
    "get": "list",
    "post": "create",
})

member_detail = CompanyMemberViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

program_course_list = CompanyProgramCourseViewSet.as_view({
    "get": "list",
    "post": "create",
})

program_course_detail = CompanyProgramCourseViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name="home"),

    path('registro/', views.register_page, name='auth.register_page'), 
    path('login/', views.login_page, name='auth.login_page'), 
    path('accounts/', include('django.contrib.auth.urls')),    

    #Api Urls Auths
    path("api/auth/register/", RegisterControllerView.as_view(), name="auth-register"),
    path("api/auth/login/", LoginControllerView.as_view(), name="auth-login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="auth-verify"),
    path("api/auth/logout/", LogoutControllerView.as_view(), name="auth-logout"),
    path("api/auth/profile/", ProfileControllerView.as_view(), name="profile"),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #Stripe
    
    
    path('api/pagos/crear/', CrearPagoView.as_view(), name='crear_pago'),

    path("api/", include(router.urls)),

    path(
        "api/course-instructors/",
        CourseInstructorListCreateAPIView.as_view(),
        name="course-instructor-list-create",
    ),
    path(
        "api/course-instructors/<int:course_id>/<int:instructor_id>/",
        CourseInstructorDetailAPIView.as_view(),
        name="course-instructor-detail",
    ),

    path("api/live-sessions/", LiveSessionListCreateView.as_view(), name="live-session-list-create"),
    path("api/live-sessions/<uuid:pk>/", LiveSessionDetailView.as_view(), name="live-session-detail"),
    path(
        "api/live-sessions/<uuid:pk>/recording/",
        LiveSessionRecordingUpdateView.as_view(),
        name="live-session-recording",
    ),

    path(
        "api/companies/<uuid:company_id>/members/", member_list, name="member-list"
    ),
    path(
        "api/companies/<uuid:company_id>/members/<uuid:user_id>/",
        member_detail,
        name="member-detail",
    ),

    path(
        "api/program-courses/",
        program_course_list,
        name="company-program-course-list",
    ),
    path(
        "api/program-courses/<int:program_id>/<int:course_id>/",
        program_course_detail,
        name="company-program-course-detail",
    ),

    path("api/lesson-progress/", LessonProgressListView.as_view(), name="lesson-progress-list"),
    path("api/lesson-progress/upsert/", LessonProgressUpsertView.as_view(), name="lesson-progress-upsert"),
    path(
        "api/lesson-progress/<int:enrollment_id>/<int:lesson_id>/",
        LessonProgressDetailView.as_view(),
        name="lesson-progress-detail",
    ),

    path(
        'api/attendance/',
        SessionAttendanceListCreateView.as_view(),
        name='session-attendance-list-create'
    ),
    # Detalle, actualizar y eliminar: /api/attendance/session/<id>/enrollment/<id>/
    path(
        'api/attendance/session/<int:session_id>/enrollment/<int:enrollment_id>/',
        SessionAttendanceDetailView.as_view(),
        name='session-attendance-detail'
    ),

    path(
        "api/answer-keys/",
        QuestionAnswerKeyListCreateView.as_view(),
        name="answer-key-list-create",
    ),
  

   
    path(
        "api/answer-keys/<int:question_id>/<int:option_id>/",
        QuestionAnswerKeyDeleteView.as_view(),
        name="answer-key-delete",
    ),

    path(
        "api/attempt-answers/",
        AttemptAnswerListUpsertView.as_view(),
        name="attempt-answer-list-upsert",
    ),
    path(
        "api/attempt-answers/<uuid:attempt_id>/<uuid:question_id>/",
        AttemptAnswerDetailView.as_view(),
        name="attempt-answer-detail",
    ),
    path("api/certificates/verify/", VerifyCertificateAPIView.as_view(), name="certificate_verify"),
    path(
        "api/reports/company-report/",
        CompanyReportViewSet.as_view({"get": "list"}),
        name="company-report-list",
    ),
    path(
        "api/reports/company-report/<uuid:company_id>/<uuid:course_id>/",
        CompanyReportViewSet.as_view({"get": "retrieve"}),
        name="company-report-detail",
    ),

    
    path("api/courses/<int:course_id>/classroom/", CourseClassroomView.as_view(), name="course-classroom"),
]