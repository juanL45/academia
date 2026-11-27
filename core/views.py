import json
from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from .models import User
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import viewsets, status, filters,permissions, generics, mixins
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from django.utils import timezone
from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from .serializers import SchoolSerializer,CustomTokenObtainPairSerializer,InstructorSerializer,CourseSerializer,CourseInstructorSerializer,CourseModuleSerializer,CourseEditionSerializer, LessonSerializer, LessonResourceSerializer, LiveSessionSerializer, LiveSessionRecordingSerializer, CompanySerializer, CompanyMemberSerializer, CompanyProgramSerializer, CompanyProgramCourseSerializer, CouponSerializer, CouponValidateSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import School, Instructor,Course,CourseInstructor,CourseEdition, PublishStatus,CourseModule, Lesson, LessonResource,LiveSession, Company, CompanyMember, CompanyMember, CompanyProgram, CompanyProgramCourse, Coupon, DiscountType
from .core_permissions import IsCompanyAdminOrReadOnly
import stripe
from django.conf import settings
from rest_framework.decorators import action
from django.db import IntegrityError, DatabaseError
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderUpdateSerializer,
    fetch_order_numbers,
    OrderItemSerializer
)
from rest_framework.exceptions import ValidationError
from .models import Order, OrderStatus, OrderItem
stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()
from .models import Payment, PaymentStatus
from .serializers import PaymentSerializer, PaymentConfirmSerializer
from .models import Enrollment
from .serializers import (
    EnrollmentListSerializer,
    EnrollmentCreateSerializer,
    EnrollmentProgressSerializer,
)

from .models import Enrollment, Lesson, LessonProgress
from .serializers import LessonProgressSerializer, LessonProgressUpsertSerializer
from .models import SessionAttendance
from .serializers import SessionAttendanceSerializer
from rest_framework.exceptions import NotFound

from .models import Assessment
from .serializers import AssessmentSerializer

from .models import Question
from .serializers import QuestionSerializer
from .models import QuestionOption
from .serializers import QuestionOptionSerializer
from .models import Question


from .models import QuestionAnswerKey
from .serializers import QuestionAnswerKeySerializer
from .core_permissions import IsTeacherOrAdmin

from .models import QuestionAnswerKey
from .serializers import QuestionAnswerKeySerializer
from .core_permissions import IsTeacherOrAdmin

from .models import AttemptAnswer
from .serializers import AttemptAnswerSerializer, AttemptAnswerGradeSerializer

from .models import Certificate, CertificateStatus
from .serializers import (
    CertificateSerializer,
    IssueCertificateSerializer,
    PublicCertificateVerificationSerializer,
    RevokeCertificateSerializer,
)
from .models import Testimonial
from .serializers import TestimonialSerializer

from .models import ContactLead
from .serializers import ContactLeadSerializer
from .models import CompanyReport, CourseStats, SalesByMonth
from .serializers import (
    CompanyReportSerializer,
    CourseStatsSerializer,
    SalesByMonthSerializer,
)

from .models import Course
from .serializers import CourseDetailSerializer
from .core_permissions import HasCourseAccessPermission
from .models import Attempt
from .serializers import AttemptSerializer
class LoginControllerView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

def issue_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("La cuenta del usuario es inactivo.")
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterControllerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        password = request.data.get("password")
        document_type = request.data.get("document_type")
        document_number = request.data.get("document_number")
        phone = request.data.get("phone")
        country = request.data.get("country")
        region = request.data.get("region")
        city = request.data.get("city")
        profession = request.data.get("profession")
        employer = request.data.get("employer")
        avatar_url = request.data.get("avatar_url")
        

        if not email or not password:
            return Response(
                {"detail": "Correo y contraseña es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(            
            email=email
            ).exists():
            return Response(
                {"detail": "Correo del usuario ya existe."},
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            document_type=document_type,
            document_number=document_number,
            phone=phone,
            country=country,
            region=region,
            city=city,
            profession=profession,
            employer=employer,
            avatar_url= avatar_url
        )
        tokens = issue_tokens_for_user(user)
        return Response(
            {
                "user": {"id": user.id, "nombres": user.first_name,"apellidos":user.last_name,  "email": user.email},
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    
class ProfileControllerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "nombres": user.first_name,
                "apellidos": user.last_name,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


class LogoutControllerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Token  es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token invalido o expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Sesion cerrada."}, status=status.HTTP_200_OK)

class CrearPagoView(APIView):
    # Exige que el usuario envíe un Token válido en el Header
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Obtenemos datos del JSON enviado por el cliente
        monto = request.data.get('monto')  # Ej: 1500 (en centavos = $15.00)
        moneda = request.data.get('moneda', 'usd')

        if not monto:
            return Response(
                {"error": "El campo 'monto' es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Creamos la intención de pago en Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(monto),
                currency=moneda,
                metadata={
                    'user_id': request.user.id,
                    'email': request.user.email
                }
            )

            # Devolvemos respuesta JSON
            return Response({
                "status": "ok",
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "usuario": request.user.email
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            return Response(
                {"error": str(e.user_message)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Error interno procesando el pago."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#Instructores
class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    
    # Autenticación mediante SimpleJWT y permiso obligatorio
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Opcional: Asigna automáticamente el usuario autenticado si no se envía en el JSON
        if not serializer.validated_data.get("user"):
            serializer.save(user=self.request.user)
        else:
            serializer.save()
      
class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    
    # Autenticación y Permisos con SimpleJWT
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]    
    # Permite buscar por 'slug' en lugar de 'id' en las URLs (opcional, quítalo si prefieres usar el UUID)
    lookup_field = "slug"
    
    # Filtros y búsqueda opcionales
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["sort_order", "name", "created_at"]
    ordering = ["sort_order"]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro opcional por query param: ?is_active=true
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        return queryset

    # Ejemplo de personalización de Response en creación
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "message": "Escuela creada exitosamente",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # Ejemplo de borrado lógico (soft delete) desactivando is_active en lugar de borrar de la BD
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(
            {"message": "Escuela desactivada correctamente"},
            status=status.HTTP_200_OK
        )
#Cursos
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related("instructors").all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Opcional: filtrar cursos del instructor autenticado si aplica
        user = self.request.user
        qs = super().get_queryset()
        if self.request.query_params.get("mine") == "true" and hasattr(user, "instructor"):
            return qs.filter(instructors=user.instructor)
        return qs

    @action(detail=True, methods=["post"], url_path="assign-instructor")
    def assign_instructor(self, request, pk=None):
        """Asigna un instructor usando el modelo intermedio CourseInstructor."""
        course = self.get_object()
        instructor_id = request.data.get("instructor_id")
        is_lead = request.data.get("is_lead", False)

        instructor = get_object_or_404(Instructor, pk=instructor_id)

        membership, created = CourseInstructor.objects.update_or_create(
            course=course,
            instructor=instructor,
            defaults={"is_lead": is_lead},
        )

        return Response(
            {
                "course_id": course.id,
                "instructor_id": instructor.id,
                "is_lead": membership.is_lead,
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
#        

class CourseInstructorListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = CourseInstructor.objects.select_related(
            "course", "instructor"
        ).all()

        # Filtros opcionales por query params (?course=1&instructor=2)
        course_id = request.query_params.get("course")
        instructor_id = request.query_params.get("instructor")

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)

        serializer = CourseInstructorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CourseInstructorSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {
                        "detail": (
                            "Conflicto de integridad en la base de datos."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseInstructorDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, course_id, instructor_id):
        # Búsqueda directa usando ambos campos de la CompositePrimaryKey
        return get_object_or_404(
            CourseInstructor.objects.select_related("course", "instructor"),
            course_id=course_id,
            instructor_id=instructor_id,
        )

    def get(self, request, course_id, instructor_id):
        instance = self.get_object(course_id, instructor_id)
        serializer = CourseInstructorSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, course_id, instructor_id):
        instance = self.get_object(course_id, instructor_id)
        # Solo permitimos actualizar 'is_lead'; las llaves primarias no deben mutarse
        data = {"is_lead": request.data.get("is_lead", instance.is_lead)}
        serializer = CourseInstructorSerializer(
            instance, data=data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, instructor_id):
        instance = self.get_object(course_id, instructor_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseEditionViewSet(viewsets.ModelViewSet):
    """
    Controlador CRUD para las ediciones de cursos (CourseEdition).
    Protegido mediante JWT (SimpleJWT).
    """
    queryset = CourseEdition.objects.select_related('course').all().order_by('-starts_on')
    serializer_class = CourseEditionSerializer

    # 1. Autenticación explícita con SimpleJWT
    authentication_classes = [JWTAuthentication]

    # 2. Permisos:
    # Usa IsAuthenticated si TODO el endpoint requiere login.
    # Usa IsAuthenticatedOrReadOnly si quieres que los GET sean públicos.
    permission_classes = [IsAuthenticated]

    # 3. Filtros y búsqueda (Opcional, pero muy útil)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'status', 'starts_on']
    search_fields = ['name', 'location', 'course__title'] # Ajusta 'course__name' según tu modelo Course
    ordering_fields = ['starts_on', 'price', 'created_at']

    def get_queryset(self):
        """
        Opcional: Filtrar registros según si el usuario está autenticado o no.
        """
        queryset = super().get_queryset()
        # Si usas IsAuthenticatedOrReadOnly, puedes ocultar los borradores a usuarios anónimos:
        if not self.request.user.is_authenticated:
            return queryset.filter(status=PublishStatus.PUBLICADO)
        return queryset

    # 4. Endpoint personalizado (Ej. PATCH /api/course-editions/{id}/publish/)
    @action(detail=True, methods=['patch'], url_path='change-status')
    def change_status(self, request, pk=None):
        """Permite cambiar rápidamente el estado de publicación de una edición."""
        edition = self.get_object()
        new_status = request.data.get('status')

        if new_status not in PublishStatus.values:
            return Response(
                {"error": f"Estado inválido. Opciones permitidas: {PublishStatus.values}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        edition.status = new_status
        edition.save(update_fields=['status'])
        serializer = self.get_serializer(edition)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseModuleViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para los módulos de un curso protegido con JWT.
    """
    serializer_class = CourseModuleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CourseModule.objects.select_related("course").all()
        
        # Filtrar por curso si se envía en la URL: /api/modules/?course=<uuid>
        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        return queryset

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        """
        Endpoint opcional para actualizar el sort_order en lote.
        Espera: [{"id": "<uuid>", "sort_order": 1}, {"id": "<uuid>", "sort_order": 2}]
        """
        items = request.data
        if not isinstance(items, list):
            return Response(
                {"detail": "Se esperaba una lista de objetos con 'id' y 'sort_order'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for item in items:
                module_id = item.get("id")
                sort_order = item.get("sort_order")
                if module_id is not None and sort_order is not None:
                    CourseModule.objects.filter(id=module_id).update(sort_order=sort_order)

        return Response({"status": "Orden actualizado correctamente."}, status=status.HTTP_200_OK)
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura (GET) a usuarios autenticados (o según lógica de preview),
    y escritura (POST, PUT, PATCH, DELETE) solo a administradores/staff.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    def get_queryset(self):
        queryset = Lesson.objects.select_related("module", "course").all()

        # Filtros opcionales por URL: ?course=<uuid>&module=<uuid>
        course_id = self.request.query_params.get("course")
        module_id = self.request.query_params.get("module")

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        return queryset.order_by("sort_order")

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        url_path="previews"
    )
    def previews(self, request):
        """
        Endpoint público para listar lecciones gratuitas (is_preview=True).
        Uso: GET /api/lessons/previews/?course=<uuid>
        """
        queryset = self.get_queryset().filter(is_preview=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonResourceViewSet(viewsets.ModelViewSet):
    """
    Controlador CRUD para LessonResource protegido con JWT.
    """
    queryset = LessonResource.objects.select_related("lesson").all().order_by("-created_at")
    serializer_class = LessonResourceSerializer
    
    # Autenticación y permisos con SimpleJWT
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        lesson_id = self.request.query_params.get("lesson")
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        return queryset
    

class BaseLiveSessionJWTView:
    """Configuración base compartida con autenticación JWT."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class LiveSessionListCreateView(BaseLiveSessionJWTView, generics.ListCreateAPIView):
    """
    GET  /api/live-sessions/  -> Lista sesiones en vivo (con filtros opcionales)
    POST /api/live-sessions/  -> Crea una nueva sesión en vivo
    """
    serializer_class = LiveSessionSerializer

    def get_queryset(self):
        queryset = LiveSession.objects.select_related(
            "course",
            "edition",
            "instructor",
        )

        params = self.request.query_params

        course_id = params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        edition_id = params.get("edition")
        if edition_id:
            queryset = queryset.filter(edition_id=edition_id)

        instructor_id = params.get("instructor")
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)

        platform = params.get("platform")
        if platform:
            queryset = queryset.filter(platform=platform)

        starts_after = params.get("starts_after")
        if starts_after:
            dt = parse_datetime(starts_after)
            if dt:
                queryset = queryset.filter(starts_at__gte=dt)

        starts_before = params.get("starts_before")
        if starts_before:
            dt = parse_datetime(starts_before)
            if dt:
                queryset = queryset.filter(starts_at__lte=dt)

        return queryset


class LiveSessionDetailView(BaseLiveSessionJWTView, generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/live-sessions/<uuid:pk>/  -> Detalle de una sesión
    PUT    /api/live-sessions/<uuid:pk>/  -> Actualización completa
    PATCH  /api/live-sessions/<uuid:pk>/  -> Actualización parcial
    DELETE /api/live-sessions/<uuid:pk>/  -> Elimina una sesión
    """
    serializer_class = LiveSessionSerializer
    queryset = LiveSession.objects.select_related("course", "edition", "instructor")


class LiveSessionRecordingUpdateView(BaseLiveSessionJWTView, APIView):
    """
    PATCH /api/live-sessions/<uuid:pk>/recording/ -> Actualiza recording_url y notes
    """
    def patch(self, request, pk):
        session = get_object_or_404(LiveSession, pk=pk)
        serializer = LiveSessionRecordingSerializer(
            session,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompanyMemberViewSet(viewsets.ModelViewSet):
  serializer_class = CompanyMemberSerializer
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsAuthenticated, IsCompanyAdminOrReadOnly]

  # Definimos el parámetro de búsqueda en la URL para el detalle
  lookup_field = "user_id"

  def get_queryset(self):
    company_id = self.kwargs.get("company_id")
    return CompanyMember.objects.filter(company_id=company_id).select_related(
        "user", "company"
    )

  def get_object(self):
    """Resuelve el objeto usando ambas partes de la CompositePrimaryKey."""
    queryset = self.filter_queryset(self.get_queryset())
    user_id = self.kwargs.get(self.lookup_field)
    obj = get_object_or_404(queryset, user_id=user_id)
    self.check_object_permissions(self.request, obj)
    return obj

  def perform_create(self, serializer):
    company_id = self.kwargs.get("company_id")
    serializer.save(company_id=company_id)

  def update(self, request, *args, **kwargs):
    # Evita que cambien el user_id o company_id en un PUT/PATCH
    partial = kwargs.pop("partial", False)
    instance = self.get_object()
    serializer = self.get_serializer(
        instance, data=request.data, partial=partial
    )
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)
    return Response(serializer.data)

class CompanyProgramViewSet(viewsets.ModelViewSet):
    """
    CRUD para CompanyProgram protegido con JWT (SimpleJWT).
    Soporta filtrado por ?company=<uuid>&status=activo y búsqueda por ?search=<texto>.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyProgramSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["company", "status"]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "starts_on", "ends_on", "total_amount", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            CompanyProgram.objects.select_related("company")
            .all()
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except (IntegrityError, DatabaseError) as exc:
            return Response(
                {"detail": f"Error de base de datos al crear el programa: {str(exc)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except (IntegrityError, DatabaseError) as exc:
            return Response(
                {"detail": f"Error de base de datos al actualizar el programa: {str(exc)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_200_OK)

class CompanyProgramCourseViewSet(viewsets.ModelViewSet):
    queryset = CompanyProgramCourse.objects.select_related(
        "program", "course", "edition"
    ).all()
    serializer_class = CompanyProgramCourseSerializer
    
    # Autenticación y permisos con SimpleJWT
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Opcional: permitir filtrar por programa desde query params (?program_id=1)
        program_id = self.request.query_params.get("program_id")
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        return queryset

    def get_object(self):
        """
        Obtiene el registro usando ambos valores de la CompositePrimaryKey
        enviados en la URL: /program-courses/<program_id>/<course_id>/
        """
        queryset = self.filter_queryset(self.get_queryset())
        program_id = self.kwargs.get("program_id")
        course_id = self.kwargs.get("course_id")

        obj = get_object_or_404(
            queryset,
            program_id=program_id,
            course_id=course_id,
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        # Evita que intenten modificar las claves primarias en un PUT/PATCH
        if "program" in request.data or "course" in request.data:
            return Response(
                {"detail": "No se pueden modificar los campos de la clave primaria (program, course)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)
class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cupones.
    - CRUD estándar: Solo administradores (IsAdminUser).
    - validate: Cualquier usuario autenticado con JWT (IsAuthenticated).
    """
    queryset = Coupon.objects.select_related("course").all().order_by("-created_at")
    serializer_class = CouponSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["validate", "redeem"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def _check_coupon_validity(self, coupon: Coupon, course_id=None):
        """Valida todas las reglas de negocio de un cupón."""
        now = timezone.now()

        if not coupon.is_active:
            return False, "Este cupón está inactivo."

        if coupon.valid_from and now < coupon.valid_from:
            return False, "Este cupón aún no es válido."

        if coupon.valid_until and now > coupon.valid_until:
            return False, "Este cupón ha expirado."

        if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
            return False, "Este cupón ha alcanzado su límite máximo de usos."

        if coupon.course_id is not None:
            if not course_id or str(coupon.course_id) != str(course_id):
                return False, "Este cupón no es válido para el curso seleccionado."

        return True, "Cupón válido."

    @action(detail=False, methods=["post"], url_path="validate")
    def validate(self, request):
        """
        Verifica si un cupón es aplicable (ideal para el carrito/checkout).
        Body esperado: {"code": "PROMO20", "course_id": "uuid-opcional"}
        """
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"].strip()
        course_id = serializer.validated_data.get("course_id")

        try:
            # iexact evita problemas si el usuario escribe en minúsculas
            coupon = Coupon.objects.select_related("course").get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response(
                {"valid": False, "detail": "El código de cupón no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_valid, message = self._check_coupon_validity(coupon, course_id)
        if not is_valid:
            return Response(
                {"valid": False, "detail": message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "valid": True,
                "detail": message,
                "coupon": {
                    "id": coupon.id,
                    "code": coupon.code,
                    "type": coupon.type,
                    "value": coupon.value,
                    "course_id": coupon.course_id,
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="redeem")
    def redeem(self, request):
        """
        Canjea el cupón de forma atómica incrementando used_count.
        Útil si lo llamas al confirmar el pago/inscripción.
        """
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"].strip()
        course_id = serializer.validated_data.get("course_id")

        with transaction.atomic():
            try:
                # Bloquea la fila en PostgreSQL hasta terminar la transacción
                coupon = Coupon.objects.select_for_update().get(code__iexact=code)
            except Coupon.DoesNotExist:
                return Response(
                    {"detail": "El código de cupón no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            is_valid, message = self._check_coupon_validity(coupon, course_id)
            if not is_valid:
                return Response(
                    {"detail": message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Incremento atómico a nivel de base de datos
            coupon.used_count = F("used_count") + 1
            coupon.save(update_fields=["used_count"])

        return Response(
            {"detail": "Cupón canjeado exitosamente."},
            status=status.HTTP_200_OK,
        )
class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Order.objects.filter(user=self.request.user)
            .select_related("user", "company", "program", "coupon")
            .order_by("-created_at")
        )
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "create":
            return OrderCreateSerializer
        if self.action in ("update", "partial_update"):
            return OrderUpdateSerializer
        return OrderDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "list":
            page = self.paginate_queryset(self.get_queryset())
            orders = page if page is not None else self.get_queryset()
            order_ids = [order.id for order in orders]
            context["order_numbers"] = fetch_order_numbers(order_ids)
        return context

    @action(detail=True, methods=["post"], url_path="pay")
    def mark_as_paid(self, request, pk=None):
        """Marca la orden como pagada y ejecuta mark_paid() (dispara trg_order_paid)."""
        order = self.get_object()

        if order.status == OrderStatus.PAGADA:
            return Response(
                {"detail": "La orden ya se encuentra pagada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(OrderStatus, "ANULADA") and order.status == OrderStatus.ANULADA:
            return Response(
                {"detail": "No se puede pagar una orden anulada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.mark_paid()

        if not order.paid_at:
            order.paid_at = timezone.now()
            order.save(update_fields=["paid_at"])

        order.refresh_from_db()
        serializer = OrderDetailSerializer(order, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)
class OrderItemViewSet(viewsets.ModelViewSet):
    """
    Controlador CRUD para los ítems de una orden (tabla: order_items).
    Protegido mediante JWT (SimpleJWT).
    """
    serializer_class = OrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OrderItem.objects.select_related(
            "order", "course", "edition"
        ).order_by("-created_at")

        # Filtro opcional por orden: GET /api/order-items/?order=<uuid>
        order_id = self.request.query_params.get("order")
        if order_id:
            queryset = queryset.filter(order_id=order_id)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            return Response(
                {"detail": "Error de integridad en base de datos.", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DatabaseError as e:
            # Captura excepciones lanzadas por triggers o constraints en PostgreSQL
            return Response(
                {"detail": "Error ejecutando la operación en base de datos.", "error": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except IntegrityError as e:
            return Response(
                {"detail": "No se puede eliminar el registro por restricciones de integridad.", "error": str(e)},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("order").all().order_by("-created_at")
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrado opcional por query params: ?order_id=...&status=...
        order_id = self.request.query_params.get("order_id")
        payment_status = self.request.query_params.get("status")

        if order_id:
            queryset = queryset.filter(order_id=order_id)
        if payment_status:
            queryset = queryset.filter(status=payment_status)

        # Si necesitas restringir para que el usuario solo vea pagos de sus propias órdenes:
        # if not self.request.user.is_staff:
        #     queryset = queryset.filter(order__user=self.request.user)

        return queryset

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm_payment(self, request, pk=None):
        """
        Endpoint: POST /api/payments/{id}/confirm/
        Marca el pago como confirmado y registra la fecha.
        """
        payment = self.get_object()

        if payment.status != PaymentStatus.PENDIENTE:
            return Response(
                {"detail": f"No se puede confirmar un pago en estado '{payment.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ajusta 'PaymentStatus.COMPLETADO' o 'PAGADO' según el nombre exacto en tu Enum
        payment.status = getattr(PaymentStatus, "PAGADO", getattr(PaymentStatus, "APROBADO", "RECHAZADO"))
        payment.confirmed_at = timezone.now()

        # Actualizar datos opcionales enviados por la pasarela o el cliente
        for field in ["provider_ref", "receipt_url", "invoice_number", "raw_response"]:
            if field in serializer.validated_data:
                setattr(payment, field, serializer.validated_data[field])

        payment.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_payment(self, request, pk=None):
        """
        Endpoint: POST /api/payments/{id}/cancel/
        Cancela un pago pendiente.
        """
        payment = self.get_object()

        if payment.status != PaymentStatus.PENDIENTE:
            return Response(
                {"detail": "Solo se pueden cancelar pagos pendientes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = getattr(PaymentStatus, "CANCELADO", "CANCELADO")
        payment.save(update_fields=["status"])
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
                              

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # Opcional: búsqueda por RUC, razón social o nombre comercial
    filter_backends = [filters.SearchFilter]
    search_fields = ["ruc", "legal_name", "trade_name"]

    def get_queryset(self):
        """
        Devuelve únicamente las empresas activas donde el usuario 
        autenticado es miembro.
        """
        user = self.request.user
        return Company.objects.filter(
            members=user,
            is_active=True
        ).distinct().order_by("-created_at")

    def perform_create(self, serializer):
        """
        Guarda la empresa y vincula al usuario creador en la tabla intermedia CompanyMember.
        """
        company = serializer.save()
        # Ajusta los campos adicionales (ej. role='admin') según tu modelo CompanyMember
        CompanyMember.objects.create(
            company=company,
            user=self.request.user
        )

    def perform_destroy(self, instance):
        """
        Borrado lógico (soft delete) cambiando is_active a False.
        Si prefieres borrado físico, elimina este método.
        """
        instance.is_active = False
        instance.save(update_fields=["is_active"])

class EnrollmentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Controlador para gestionar inscripciones (Enrollments).
    Requiere token JWT válido en el header: Authorization: Bearer <token>
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = Enrollment.objects.select_related(
            "user", "course", "edition", "company", "program", "order_item"
        ).order_by("-enrolled_at")

        # Si es administrador ve todo; si es estudiante, solo sus inscripciones
        if user.is_staff:
            return base_qs
        return base_qs.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return EnrollmentCreateSerializer
        if self.action == "update_progress":
            return EnrollmentProgressSerializer
        return EnrollmentListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        
        # Devolvemos la respuesta formateada con el serializer de lectura
        read_serializer = EnrollmentListSerializer(enrollment)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="progress")
    def update_progress(self, request, pk=None):
        """
        Endpoint personalizado: PATCH /api/enrollments/{id}/progress/
        Permite actualizar el porcentaje de avance del curso.
        """
        enrollment = self.get_object()

        if not enrollment.has_access and not request.user.is_staff:
            return Response(
                {"detail": "No tienes acceso activo a esta inscripción."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(enrollment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_enrollment = serializer.save()

        return Response(EnrollmentListSerializer(updated_enrollment).data)
    
class LessonProgressListView(APIView):
    """
    GET /api/lesson-progress/?enrollment=<id>
    Lista el progreso de lecciones del usuario autenticado.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            LessonProgress.objects.select_related("enrollment", "lesson")
            .filter(enrollment__user=request.user)
            .order_by("-updated_at")
        )

        enrollment_id = request.query_params.get("enrollment")
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)

        serializer = LessonProgressSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonProgressUpsertView(APIView):
    """
    PUT / PATCH / POST /api/lesson-progress/
    Crea o actualiza el progreso de una lección para (enrollment, lesson).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _upsert(self, request, partial=False):
        enrollment_id = request.data.get("enrollment")
        lesson_id = request.data.get("lesson")

        instance = None
        if enrollment_id and lesson_id:
            instance = LessonProgress.objects.filter(
                enrollment_id=enrollment_id,
                lesson_id=lesson_id,
                enrollment__user=request.user,
            ).first()

        serializer = LessonProgressUpsertSerializer(
            instance=instance,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        progress = serializer.save()

        # Si necesitas leer campos recalculados por el trigger trg_progress en Enrollment,
        # puedes refrescar la relación si lo deseas:
        # progress.enrollment.refresh_from_db()

        output = LessonProgressSerializer(progress)
        http_status = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        return Response(output.data, status=http_status)

    def post(self, request):
        return self._upsert(request, partial=False)

    def put(self, request):
        return self._upsert(request, partial=False)

    def patch(self, request):
        return self._upsert(request, partial=True)


class LessonProgressDetailView(APIView):
    """
    GET / PATCH / DELETE /api/lesson-progress/<int:enrollment_id>/<int:lesson_id>/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_object(self, request, enrollment_id, lesson_id):
        get_object_or_404(Enrollment, pk=enrollment_id, user=request.user)
        get_object_or_404(Lesson, pk=lesson_id)
        return get_object_or_404(
            LessonProgress.objects.select_related("enrollment", "lesson"),
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
        )

    def get(self, request, enrollment_id, lesson_id):
        progress = self._get_object(request, enrollment_id, lesson_id)
        return Response(LessonProgressSerializer(progress).data, status=status.HTTP_200_OK)

    def patch(self, request, enrollment_id, lesson_id):
        progress = self._get_object(request, enrollment_id, lesson_id)
        payload = {
            **request.data,
            "enrollment": enrollment_id,
            "lesson": lesson_id,
        }
        serializer = LessonProgressUpsertSerializer(
            instance=progress,
            data=payload,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(LessonProgressSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, enrollment_id, lesson_id):
        progress = self._get_object(request, enrollment_id, lesson_id)
        progress.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class SessionAttendanceListCreateView(generics.ListCreateAPIView):
    """
    GET: Lista asistencias (permite filtrar por ?session=ID o ?enrollment=ID).
    POST: Registra una nueva asistencia asignando el usuario JWT actual a 'recorded_by'.
    """
    queryset = SessionAttendance.objects.select_related('session', 'enrollment', 'recorded_by').all()
    serializer_class = SessionAttendanceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # Filtros útiles por query params
    filterset_fields = ['session', 'enrollment', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrado manual básico por si no tienes instalado django-filter
        session_id = self.request.query_params.get('session')
        enrollment_id = self.request.query_params.get('enrollment')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class SessionAttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH, DELETE usando la llave primaria compuesta (session_id + enrollment_id).
    """
    queryset = SessionAttendance.objects.select_related('session', 'enrollment', 'recorded_by').all()
    serializer_class = SessionAttendanceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        session_id = self.kwargs.get('session_id')
        enrollment_id = self.kwargs.get('enrollment_id')
        
        try:
            # Django 5.2+ permite buscar directamente por pk=(val1, val2) o por los campos
            return self.get_queryset().get(session_id=session_id, enrollment_id=enrollment_id)
        except SessionAttendance.DoesNotExist:
            raise NotFound("No se encontró el registro de asistencia para esta sesión e inscripción.")

    def perform_update(self, serializer):
        # Actualiza también quién modificó el registro
        serializer.save(recorded_by=self.request.user)

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.select_related("course", "module").all().order_by("-created_at")
    serializer_class = AssessmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales por query params: ?course_id=...&module_id=...
        course_id = self.request.query_params.get("course_id")
        module_id = self.request.query_params.get("module_id")

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        return queryset
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("assessment").all()
    serializer_class = QuestionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrado opcional por assessment: /api/questions/?assessment=<uuid>
        assessment_id = self.request.query_params.get("assessment")
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)
        return queryset

    # Endpoint extra opcional para reordenar preguntas en lote:
    # PATCH /api/questions/reorder/ -> [{"id": "uuid", "sort_order": 1}, ...]
    @action(detail=False, methods=["patch"], url_path="reorder")
    def reorder(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response(
                {"detail": "Se esperaba una lista de objetos con 'id' y 'sort_order'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for item in items:
            Question.objects.filter(id=item.get("id")).update(
                sort_order=item.get("sort_order", 0)
            )

        return Response({"detail": "Orden actualizado correctamente."}, status=status.HTTP_200_OK)



class QuestionAnswerKeyDeleteView(APIView):
    """
    DELETE: Elimina una respuesta correcta usando ambos valores de la clave compuesta.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacherOrAdmin]

    def delete(self, request, question_id, option_id):
        instance = get_object_or_404(
            QuestionAnswerKey,
            question_id=question_id,
            option_id=option_id
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
           
class QuestionAnswerKeyListCreateView(APIView):
    """
    GET: Lista las respuestas correctas (filtrable por ?question=<id>).
    POST: Asigna una opción como respuesta correcta para una pregunta.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        queryset = QuestionAnswerKey.objects.all()
        question_id = request.query_params.get("question")
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        serializer = QuestionAnswerKeySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = QuestionAnswerKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        question = serializer.validated_data["question"]
        option = serializer.validated_data["option"]

        # Evita error de llave duplicada en tablas unmanaged
        obj, created = QuestionAnswerKey.objects.get_or_create(
            question=question,
            option=option
        )
        out_serializer = QuestionAnswerKeySerializer(obj)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(out_serializer.data, status=status_code)


class QuestionAnswerKeyDeleteView(APIView):
    """
    DELETE: Elimina una respuesta correcta usando ambos valores de la clave compuesta.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacherOrAdmin]

    def delete(self, request, question_id, option_id):
        instance = get_object_or_404(
            QuestionAnswerKey,
            question_id=question_id,
            option_id=option_id
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class AttemptAnswerListUpsertView(APIView):
    """
    GET: Lista todas las respuestas de un intento (?attempt=<uuid>) del usuario autenticado.
    POST: Crea o actualiza (upsert) la respuesta para (attempt, question).
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempt_id = request.query_params.get("attempt")
        queryset = AttemptAnswer.objects.select_related("attempt", "question").filter(
            attempt__user=request.user
        )
        if attempt_id:
            queryset = queryset.filter(attempt_id=attempt_id)

        serializer = AttemptAnswerSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AttemptAnswerSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        attempt = serializer.validated_data["attempt"]
        question = serializer.validated_data["question"]

        # Upsert seguro sobre la llave primaria compuesta (attempt, question)
        instance, created = AttemptAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "option_ids": serializer.validated_data.get("option_ids", []),
                "text_answer": serializer.validated_data.get("text_answer"),
            },
        )

        output = AttemptAnswerSerializer(instance)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class AttemptAnswerDetailView(APIView):
    """
    Maneja una respuesta específica mediante su llave compuesta en la URL:
    /attempt-answers/<uuid:attempt_id>/<uuid:question_id>/
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, request, attempt_id, question_id):
        return get_object_or_404(
            AttemptAnswer.objects.select_related("attempt", "question"),
            attempt_id=attempt_id,
            question_id=question_id,
            attempt__user=request.user,
        )

    def get(self, request, attempt_id, question_id):
        obj = self.get_object(request, attempt_id, question_id)
        serializer = AttemptAnswerSerializer(obj)
        return Response(serializer.data)

    def patch(self, request, attempt_id, question_id):
        obj = self.get_object(request, attempt_id, question_id)

        if hasattr(obj.attempt, "submitted_at") and obj.attempt.submitted_at is not None:
            return Response(
                {"detail": "El intento ya fue enviado; no se puede modificar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AttemptAnswerSerializer(
            obj, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Actualizamos solo los campos editables de respuesta
        if "option_ids" in serializer.validated_data:
            obj.option_ids = serializer.validated_data["option_ids"]
        if "text_answer" in serializer.validated_data:
            obj.text_answer = serializer.validated_data["text_answer"]
        obj.save(update_fields=["option_ids", "text_answer"])

        return Response(AttemptAnswerSerializer(obj).data)

    def delete(self, request, attempt_id, question_id):
        obj = self.get_object(request, attempt_id, question_id)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Controlador autenticado con JWT:
    - GET /api/certificates/ -> Lista certificados del usuario (o todos si es staff)
    - GET /api/certificates/{id}/ -> Detalle de un certificado
    - POST /api/certificates/issue/ -> Emite certificado usando Certificate.issue()
    - POST /api/certificates/{id}/revoke/ -> Revoca certificado (solo staff)
    """

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Certificate.objects.select_related("enrollment", "user", "course")
        if user.is_staff:
            return qs.order_by("-issued_at")
        return qs.filter(user=user).order_by("-issued_at")

    @action(detail=False, methods=["post"], url_path="issue")
    def issue_certificate(self, request):
        serializer = IssueCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment_id = serializer.validated_data["enrollment_id"]

        try:
            with transaction.atomic():
                cert = Certificate.issue(enrollment_id)
        except DatabaseError as exc:
            raise ValidationError(
                {"detail": f"No se pudo emitir el certificado: {str(exc)}"}
            ) from exc
        except IndexError as exc:
            raise ValidationError(
                {"detail": "La función issue_certificate no devolvió ningún registro."}
            ) from exc

        output = CertificateSerializer(cert, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="revoke",
        permission_classes=[IsAuthenticated, IsAdminOrStaff],
    )
    def revoke_certificate(self, request, pk=None):
        certificate = self.get_object()
        serializer = RevokeCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if certificate.status == CertificateStatus.REVOCADO:
            return Response(
                {"detail": "El certificado ya se encuentra revocado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        certificate.status = CertificateStatus.REVOCADO
        certificate.revoked_at = timezone.now()
        certificate.revoked_reason = serializer.validated_data["revoked_reason"]
        certificate.save(update_fields=["status", "revoked_at", "revoked_reason"])

        return Response(
            CertificateSerializer(certificate, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class VerifyCertificateAPIView(APIView):
    """
    Endpoint público de verificación:
    GET /api/certificates/verify/?code=ABC123
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        code = request.query_params.get("code", "").strip()
        if not code:
            return Response(
                {"detail": "El parámetro 'code' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cert = Certificate.verify(code)
        if not cert:
            return Response(
                {"valid": False, "detail": "Certificado no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = PublicCertificateVerificationSerializer(cert).data
        return Response(
            {
                "valid": cert.status == CertificateStatus.VIGENTE,
                "certificate": data,
            },
            status=status.HTTP_200_OK,
        )
class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().order_by("-created_at")
    serializer_class = TestimonialSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class ContactLeadViewSet(viewsets.ModelViewSet):
    queryset = ContactLead.objects.all().order_by("-created_at")
    serializer_class = ContactLeadSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Opcional: Búsqueda y ordenamiento por query params (?search=juan&ordering=created_at)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "email", "company", "phone"]
    ordering_fields = ["created_at", "handled", "full_name"]

    # Descomenta este método si quieres que cualquiera pueda enviar un formulario (POST),
    # pero que solo usuarios autenticados puedan ver, editar o borrar leads.
    """
    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]
    """

    @action(detail=True, methods=["patch"], url_path="toggle-handled")
    def toggle_handled(self, request, pk=None):
        """Alterna el estado 'handled' (True/False) del lead."""
        lead = self.get_object()
        lead.handled = not lead.handled
        lead.save(update_fields=["handled"])
        serializer = self.get_serializer(lead)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BaseReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class SalesByMonthViewSet(BaseReadOnlyViewSet):
    queryset = SalesByMonth.objects.all().order_by("-month")
    serializer_class = SalesByMonthSerializer
    lookup_field = "month"


class CourseStatsViewSet(BaseReadOnlyViewSet):
    queryset = CourseStats.objects.all().order_by("title")
    serializer_class = CourseStatsSerializer
    lookup_field = "course_id"


class CompanyReportViewSet(BaseReadOnlyViewSet):
    queryset = CompanyReport.objects.all().order_by("legal_name", "course")
    serializer_class = CompanyReportSerializer

    def get_object(self):
        company_id = self.kwargs.get("company_id")
        course_id = self.kwargs.get("course_id")
        obj = get_object_or_404(
            self.get_queryset(),
            company_id=company_id,
            course_id=course_id,
        )
        self.check_object_permissions(self.request, obj)
        return obj
    
class CourseClassroomView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasCourseAccessPermission]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        
        # Dispara HasCourseAccessPermission.has_object_permission()
        self.check_object_permissions(request, course)

        serializer = CourseDetailSerializer(course, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
class AttemptViewSet(viewsets.ModelViewSet):
    serializer_class = AttemptSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Si es staff/admin ve todos los intentos; si es estudiante, solo los suyos
        user = self.request.user
        qs = Attempt.objects.select_related("assessment", "enrollment", "user")
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="grade")
    def grade_attempt(self, request, pk=None):
        """
        POST /api/attempts/{id}/grade/
        Marca el intento como enviado (si no lo estaba) y ejecuta grade_attempt() en PostgreSQL.
        """
        attempt = self.get_object()

        if attempt.submitted_at is not None and not request.user.is_staff:
            return Response(
                {"detail": "Este intento ya fue enviado y calificado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if attempt.submitted_at is None:
                attempt.submitted_at = timezone.now()
                attempt.save(update_fields=["submitted_at"])

            # Invoca el método del modelo que llama a PostgreSQL
            attempt.grade()

        serializer = self.get_serializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
def login_page(request):
    if request.method == 'POST':
        next_url = request.POST.get('next')
        username =request.POST.get('username')
        password =request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if next_url:
                return redirect(next_url)
            else:                
                return redirect('/')
        else:
            messages.warning(request, 'No te has podido identificar :)')
    return render(request, 'auth/login.html')


def register_page(request):    
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Te has registrado correctamente')
            return redirect('/') 
    else:
        # Se instancia un formulario vacío cuando la petición es GET
        register_form = RegisterForm()

    return render(request, 'auth/register.html', {
        'register_form': register_form
    })

# Create your views here.
@login_required
def home(request):
    return render(request,'home.html')



class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    
    # Autenticación explícita con SimpleJWT (opcional si ya está en settings.py)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        question_id = self.request.query_params.get("question")
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        return queryset