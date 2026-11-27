from django.db import connection
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import School, Instructor,Course,CourseInstructor,CourseEdition,CourseModule, Lesson, LessonResource, LiveSession, Company,CompanyMember, CompanyRole, CompanyProgram, CompanyProgramCourse, Coupon, Order, OrderStatus, OrderItem, Order, Course, CourseEdition, Payment, PaymentStatus
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Enrollment, EnrollmentStatus
from django.utils import timezone
from .models import Enrollment, Lesson, LessonProgress
from .models import SessionAttendance
from .models import Question, QuestionType
from .models import Assessment
from .models import QuestionOption
from .models import Question, QuestionOption, QuestionAnswerKey
from .models import AttemptAnswer, Attempt, Question
from .models import QuestionAnswerKey
from .models import Certificate
from .models import Testimonial
from .models import ContactLead
from .models import CompanyReport, CourseStats, SalesByMonth


from .core_permissions import has_course_access

from .models import Attempt

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims embedded inside the encoded JWT
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Extra fields returned in the HTTP response JSON body
        data["user"] = {
            "id": self.user.id,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
        }
        return data

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "icon",
            "color",
            "sort_order",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = [
            "id",
            "user",
            "full_name",
            "headline",
            "bio",
            "photo_url",
            "linkedin_url",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "school",
            "slug",
            "title",
            "short_description",
            "description",
            "objectives",
            "target_audience",
            "requirements",
            "syllabus",
            "duration_hours",
            "modality",
            "level",
            "price",
            "currency",
            "thumbnail_url",
            "promo_video_url",
            "passing_score",
            "issues_certificate",
            "access_days",
            "is_featured",
            "status",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
class CourseInstructorSerializer(serializers.ModelSerializer):
    # Campos de solo lectura opcionales para enriquecer la respuesta JSON
    course_title = serializers.CharField(source="course.title", read_only=True)
    instructor_name = serializers.CharField(
        source="instructor.full_name", read_only=True
    )

    class Meta:
        model = CourseInstructor
        fields = [
            "course",
            "course_title",
            "instructor",
            "instructor_name",
            "is_lead",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=CourseInstructor.objects.all(),
                fields=["course", "instructor"],
                message="Este instructor ya está asignado a este curso.",
            )
        ]

class CourseEditionSerializer(serializers.ModelSerializer):
    # Opcional: para mostrar el nombre del curso en respuestas GET sin perder el ID al hacer POST/PUT
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = CourseEdition
        fields = [
            'id',
            'course',
            'course_title',
            'name',
            'starts_on',
            'ends_on',
            'capacity',
            'price',
            'location',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        """Validación personalizada para fechas."""
        starts_on = data.get('starts_on')
        ends_on = data.get('ends_on')
        if starts_on and ends_on and ends_on < starts_on:
            raise serializers.ValidationError({
                "ends_on": "La fecha de finalización no puede ser anterior a la fecha de inicio."
            })
        return data

class CourseModuleSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = CourseModule
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "sort_order",
        ]
        read_only_fields = ["id"]

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "module",
            "course",
            "title",
            "type",
            "video_provider",
            "video_ref",
            "content",
            "duration_minutes",
            "is_preview",
            "is_required",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Asegura que el módulo pertenezca al curso enviado (si ambos están presentes)
        module = attrs.get("module") or getattr(self.instance, "module", None)
        course = attrs.get("course") or getattr(self.instance, "course", None)

        if module and course and module.course_id != course.id:
            raise serializers.ValidationError(
                {"module": "El módulo seleccionado no pertenece al curso especificado."}
            )
        return attrs

class LessonResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonResource
        fields = [
            "id",
            "lesson",
            "title",
            "file_path",
            "file_type",
            "size_bytes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = [
            "id",
            "course",
            "edition",
            "instructor",
            "title",
            "platform",
            "meeting_url",
            "meeting_code",
            "starts_at",
            "ends_at",
            "recording_url",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))

        if starts_at and ends_at and ends_at < starts_at:
            raise serializers.ValidationError(
                {"ends_at": "La fecha/hora de fin no puede ser anterior a la de inicio."}
            )
        return attrs


class LiveSessionRecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = ["id", "recording_url", "notes"]
        read_only_fields = ["id"]

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "ruc",
            "legal_name",
            "trade_name",
            "sector",
            "contact_name",
            "contact_email",
            "contact_phone",
            "address",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class CompanyMemberSerializer(serializers.ModelSerializer):
  # Opcional: mostrar datos básicos del usuario en lugar de solo el ID
  user_email = serializers.EmailField(source="user.email", read_only=True)

  class Meta:
    model = CompanyMember
    fields = [
        "company",
        "user",
        "user_email",
        "role",
        "job_title",
        "area",
        "created_at",
    ]
    read_only_fields = ["company", "created_at"]

  def validate(self, attrs):
    # Evitar duplicados si se crea mediante el endpoint anidado
    request = self.context.get("request")
    view = self.context.get("view")
    if request and request.method == "POST" and view:
      company_id = view.kwargs.get("company_id")
      user = attrs.get("user")
      if CompanyMember.objects.filter(
          company_id=company_id, user=user
      ).exists():
        raise serializers.ValidationError(
            {"user": "Este usuario ya es miembro de la empresa."}
        )
    return attrs


class CompanyProgramSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)

    class Meta:
        model = CompanyProgram
        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "starts_on",
            "ends_on",
            "total_amount",
            "notes",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        starts_on = attrs.get("starts_on", getattr(self.instance, "starts_on", None))
        ends_on = attrs.get("ends_on", getattr(self.instance, "ends_on", None))

        if starts_on and ends_on and ends_on < starts_on:
            raise serializers.ValidationError(
                {"ends_on": "La fecha de finalización no puede ser anterior a la fecha de inicio."}
            )
        return attrs

class CompanyProgramCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProgramCourse
        fields = ["program", "course", "edition", "seats"]

    def validate(self, attrs):
        # En creación (POST), validamos manualmente que no exista el par compuesto
        if self.instance is None:
            program = attrs.get("program")
            course = attrs.get("course")
            if CompanyProgramCourse.objects.filter(program=program, course=course).exists():
                raise serializers.ValidationError(
                    "Este curso ya está asignado a este programa."
                )
        return attrs

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ("id", "used_count", "created_at")


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)
    course_id = serializers.UUIDField(required=False, allow_null=True)

def fetch_order_numbers(order_ids: list) -> dict:
    """Obtiene order_number (GENERATED ALWAYS AS IDENTITY) vía SQL crudo."""
    if not order_ids:
        return {}
    placeholders = ", ".join(["%s"] * len(order_ids))
    sql = f"SELECT id, order_number FROM orders WHERE id IN ({placeholders})"
    with connection.cursor() as cursor:
        cursor.execute(sql, [str(oid) for oid in order_ids])
        return {str(row[0]): row[1] for row in cursor.fetchall()}


class OrderListSerializer(serializers.ModelSerializer):
    order_number = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    company_name = serializers.CharField(source="company.legal_name", read_only=True, default=None)
    program_name = serializers.CharField(source="program.name", read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "user_email",
            "company",
            "company_name",
            "program",
            "program_name",
            "subtotal",
            "discount",
            "total",
            "currency",
            "status",
            "created_at",
            "paid_at",
        ]
        read_only_fields = fields

    def get_order_number(self, obj):
        order_numbers = self.context.get("order_numbers")
        if order_numbers is not None:
            return order_numbers.get(str(obj.id))
        return fetch_order_numbers([obj.id]).get(str(obj.id))


class OrderDetailSerializer(OrderListSerializer):
    coupon_code = serializers.CharField(source="coupon.code", read_only=True, default=None)

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + [
            "coupon",
            "coupon_code",
            "billing_name",
            "billing_doc",
            "notes",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
    order_number = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "company",
            "program",
            "coupon",
            "subtotal",
            "discount",
            "total",
            "currency",
            "billing_name",
            "billing_doc",
            "notes",
            "status",
            "created_at",
            "paid_at",
        ]
        read_only_fields = ["id", "order_number", "status", "created_at", "paid_at"]

    def get_order_number(self, obj):
        return fetch_order_numbers([obj.id]).get(str(obj.id))

    def validate_subtotal(self, value):
        if value < 0:
            raise serializers.ValidationError("El subtotal no puede ser negativo.")
        return value

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError("El descuento no puede ser negativo.")
        return value

    def validate(self, attrs):
        subtotal = attrs.get("subtotal", 0)
        discount = attrs.get("discount", 0)
        total = attrs.get("total", 0)

        if discount > subtotal:
            raise serializers.ValidationError(
                {"discount": "El descuento no puede superar el subtotal."}
            )
        if total < 0:
            raise serializers.ValidationError(
                {"total": "El total no puede ser negativo."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["user"] = request.user
        validated_data["status"] = OrderStatus.PENDIENTE
        return super().create(validated_data)


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Permite editar datos de facturación o notas solo mientras esté pendiente."""

    class Meta:
        model = Order
        fields = [
            "billing_name",
            "billing_doc",
            "notes",
        ]

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.status != OrderStatus.PENDIENTE:
            raise serializers.ValidationError(
                "Solo se pueden modificar órdenes en estado pendiente."
            )
        return attrs

class OrderItemSerializer(serializers.ModelSerializer):
    # Campos informativos de solo lectura (opcionales pero útiles en el frontend)
    course_title = serializers.CharField(source="course.title", read_only=True)
    edition_name = serializers.CharField(source="edition.name", read_only=True, default=None)
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "course",
            "course_title",
            "edition",
            "edition_name",
            "quantity",
            "unit_price",
            "subtotal",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "subtotal"]

    def get_subtotal(self, obj):
        return obj.quantity * obj.unit_price

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio unitario no puede ser negativo.")
        return value

    def validate(self, attrs):
        """
        Validación cruzada: si se envía una edición, verificar que pertenezca al curso.
        """
        course = attrs.get("course", getattr(self.instance, "course", None))
        edition = attrs.get("edition", getattr(self.instance, "edition", None))

        if edition and course and edition.course_id != course.id:
            raise serializers.ValidationError(
                {"edition": "La edición seleccionada no pertenece al curso indicado."}
            )
        return attrs

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "provider",
            "provider_ref",
            "amount",
            "currency",
            "status",
            "receipt_url",
            "invoice_number",
            "raw_response",
            "created_at",
            "confirmed_at",
        ]
        # Campos que no deberían ser modificados directamente en la creación
        read_only_fields = ["id", "status", "created_at", "confirmed_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto del pago debe ser mayor a 0.")
        return value


class PaymentConfirmSerializer(serializers.Serializer):
    """Serializer específico para la acción de confirmar un pago."""
    provider_ref = serializers.CharField(required=False, allow_blank=True)
    receipt_url = serializers.URLField(required=False, allow_blank=True)
    invoice_number = serializers.CharField(required=False, allow_blank=True)
    raw_response = serializers.JSONField(required=False)

class EnrollmentListSerializer(serializers.ModelSerializer):
    """Serializer para listar y ver detalle de inscripciones."""
    has_access = serializers.BooleanField(read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True) # Ajusta 'title' al campo de tu modelo Course
    edition_name = serializers.CharField(source="edition.name", read_only=True, default=None)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "course",
            "course_title",
            "edition",
            "edition_name",
            "company",
            "program",
            "status",
            "progress_percent",
            "enrolled_at",
            "access_until",
            "completed_at",
            "has_access",
        ]
        read_only_fields = fields


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer para que un usuario autenticado cree su propia inscripción."""
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "edition",
            "order_item",
            "company",
            "program",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = self.context["request"].user
        course = attrs.get("course")
        edition = attrs.get("edition")

        # Validación equivalente al índice único de la BD (coalesce(edition_id, uuid_nulo))
        queryset = Enrollment.objects.filter(user=user, course=course)
        if edition:
            queryset = queryset.filter(edition=edition)
        else:
            queryset = queryset.filter(edition__isnull=True)

        if queryset.exists():
            raise serializers.ValidationError(
                "El usuario ya se encuentra inscrito en este curso/edición."
            )

        # Validar que la edición pertenezca al curso enviado
        if edition and edition.course_id != course.id:
            raise serializers.ValidationError(
                {"edition": "La edición seleccionada no pertenece al curso indicado."}
            )

        return attrs

    def create(self, validated_data):
        # Asignamos automáticamente el usuario autenticado del token JWT
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class EnrollmentProgressSerializer(serializers.ModelSerializer):
    """Serializer para actualizar el progreso del estudiante."""
    class Meta:
        model = Enrollment
        fields = ["progress_percent"]

    def validate_progress_percent(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El progreso debe estar entre 0 y 100.")
        return value

    def update(self, instance, validated_data):
        from django.utils import timezone
        
        progress = validated_data.get("progress_percent", instance.progress_percent)
        instance.progress_percent = progress

        # Si llega al 100%, marcamos como completada automáticamente
        if progress == 100 and instance.status != EnrollmentStatus.COMPLETADA:
            instance.status = EnrollmentStatus.COMPLETADA
            instance.completed_at = timezone.now()

        instance.save(update_fields=["progress_percent", "status", "completed_at"])
        return instance

class LessonProgressSerializer(serializers.ModelSerializer):
    enrollment_id = serializers.PrimaryKeyRelatedField(
        source="enrollment", read_only=True
    )
    lesson_id = serializers.PrimaryKeyRelatedField(
        source="lesson", read_only=True
    )

    class Meta:
        model = LessonProgress
        fields = [
            "enrollment_id",
            "lesson_id",
            "completed",
            "last_position_secs",
            "completed_at",
            "updated_at",
        ]
        read_only_fields = ["completed_at", "updated_at"]


class LessonProgressUpsertSerializer(serializers.ModelSerializer):
    enrollment = serializers.PrimaryKeyRelatedField(queryset=Enrollment.objects.all())
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())

    class Meta:
        model = LessonProgress
        fields = [
            "enrollment",
            "lesson",
            "completed",
            "last_position_secs",
        ]

    def validate_last_position_secs(self, value):
        if value < 0:
            raise serializers.ValidationError("last_position_secs no puede ser negativo.")
        return value

    def validate(self, attrs):
        enrollment = attrs.get("enrollment") or getattr(self.instance, "enrollment", None)
        lesson = attrs.get("lesson") or getattr(self.instance, "lesson", None)

        # Verifica que el usuario autenticado sea dueño del enrollment
        request = self.context.get("request")
        if request and enrollment and enrollment.user_id != request.user.id:
            raise serializers.ValidationError(
                {"enrollment": "No tienes permiso sobre esta inscripción."}
            )

        # Verifica coherencia curso <-> lección (ajusta el nombre del campo según tu modelo Lesson/Enrollment)
        if enrollment and lesson:
            enrollment_course_id = getattr(enrollment, "course_id", None)
            lesson_course_id = getattr(lesson, "course_id", None)
            if (
                enrollment_course_id is not None
                and lesson_course_id is not None
                and enrollment_course_id != lesson_course_id
            ):
                raise serializers.ValidationError(
                    {"lesson": "La lección no pertenece al curso de esta inscripción."}
                )

        return attrs

    def create(self, validated_data):
        now = timezone.now()
        completed = validated_data.get("completed", False)
        validated_data["updated_at"] = now
        validated_data["completed_at"] = now if completed else None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        now = timezone.now()
        completed = validated_data.get("completed", instance.completed)

        validated_data["updated_at"] = now
        if completed and not instance.completed_at:
            validated_data["completed_at"] = now
        elif not completed:
            validated_data["completed_at"] = None

        return super().update(instance, validated_data)

class SessionAttendanceSerializer(serializers.ModelSerializer):
    # Campos informativos opcionales de solo lectura
    recorded_by_email = serializers.ReadOnlyField(source='recorded_by.email')

    class Meta:
        model = SessionAttendance
        fields = [
            'session',
            'enrollment',
            'status',
            'joined_at',
            'left_at',
            'recorded_by',
            'recorded_by_email',
        ]
        read_only_fields = ['recorded_by']

    def validate(self, attrs):
        # Validar que left_at no sea anterior a joined_at
        joined_at = attrs.get('joined_at', getattr(self.instance, 'joined_at', None))
        left_at = attrs.get('left_at', getattr(self.instance, 'left_at', None))

        if joined_at and left_at and left_at < joined_at:
            raise serializers.ValidationError({
                "left_at": "La hora de salida no puede ser anterior a la hora de entrada."
            })
        return attrs

    def update(self, instance, validated_data):
        # Evitar que se altere la llave primaria compuesta durante una actualización
        validated_data.pop('session', None)
        validated_data.pop('enrollment', None)
        return super().update(instance, validated_data)

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = [
            "id",
            "course",
            "module",
            "title",
            "instructions",
            "is_final",
            "passing_score",
            "max_attempts",
            "time_limit_minutes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        course = attrs.get("course", getattr(self.instance, "course", None))
        module = attrs.get("module", getattr(self.instance, "module", None))

        # Validar que el módulo pertenezca al curso seleccionado
        if module and course and module.course_id != course.id:
            raise serializers.ValidationError({
                "module": "El módulo seleccionado no pertenece al curso indicado."
            })

        return attrs

class QuestionSerializer(serializers.ModelSerializer):
    # Muestra la etiqueta legible del Enum en respuestas GET (ej. "Opción Única")
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "assessment",
            "type",
            "type_display",
            "statement",
            "points",
            "explanation",
            "sort_order",
        ]
        read_only_fields = ["id"]

    def validate_points(self, value):
        if value < 0:
            raise serializers.ValidationError("Los puntos no pueden ser negativos.")
        return value

    def validate_type(self, value):
        if value not in QuestionType.values:
            raise serializers.ValidationError("Tipo de pregunta inválido.")
        return value

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "question", "text", "sort_order"]
        read_only_fields = ["id"]

class QuestionAnswerKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswerKey
        fields = ["question", "option"]

    def validate(self, attrs):
        question = attrs.get("question")
        option = attrs.get("option")

        # Verifica que la opción pertenezca a la pregunta (asumiendo que QuestionOption tiene FK 'question')
        if option.question_id != question.id:
            raise serializers.ValidationError(
                {"option": "La opción seleccionada no pertenece a esta pregunta."}
            )
        return attrs



class AttemptAnswerSerializer(serializers.ModelSerializer):
    # Exponemos explícitamente los IDs para lectura/escritura limpia
    attempt_id = serializers.UUIDField(source="attempt.id", read_only=True)
    question_id = serializers.UUIDField(source="question.id", read_only=True)

    attempt = serializers.PrimaryKeyRelatedField(
        queryset=Attempt.objects.all(), write_only=True
    )
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), write_only=True
    )
    option_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        default=list,
    )

    class Meta:
        model = AttemptAnswer
        fields = [
            "attempt",
            "question",
            "attempt_id",
            "question_id",
            "option_ids",
            "text_answer",
            "is_correct",
            "points_awarded",
        ]
        # Evitamos que el cliente manipule la calificación directamente al responder
        read_only_fields = ["is_correct", "points_awarded"]

    def validate(self, attrs):
        attempt = attrs.get("attempt")
        question = attrs.get("question")
        request = self.context.get("request")

        # 1. Validar que el intento pertenezca al usuario autenticado (ajusta 'user' según tu modelo Attempt)
        if request and hasattr(attempt, "user") and attempt.user != request.user:
            raise serializers.ValidationError(
                {"attempt": "No tienes permiso para modificar este intento."}
            )

        # 2. Validar que el intento siga abierto/en progreso (ajusta el estado según tu lógica)
        if hasattr(attempt, "submitted_at") and attempt.submitted_at is not None:
            raise serializers.ValidationError(
                {"attempt": "Este intento ya fue finalizado y no acepta cambios."}
            )

        # 3. Validar que la pregunta pertenezca a la misma evaluación del intento (si aplica)
        if (
            hasattr(attempt, "quiz_id")
            and hasattr(question, "quiz_id")
            and attempt.quiz_id != question.quiz_id
        ):
            raise serializers.ValidationError(
                {"question": "La pregunta no pertenece a la evaluación de este intento."}
            )

        return attrs


class AttemptAnswerGradeSerializer(serializers.ModelSerializer):
    """Serializer opcional para calificación manual por parte de un instructor."""

    class Meta:
        model = AttemptAnswer
        fields = ["is_correct", "points_awarded"]

class CertificateSerializer(serializers.ModelSerializer):
    """Lectura completa para usuarios autenticados o administradores."""

    class Meta:
        model = Certificate
        fields = [
            "id",
            "enrollment",
            "user",
            "course",
            "certificate_no",
            "verification_code",
            "participant_name",
            "participant_doc",
            "course_title",
            "hours",
            "modality",
            "training_start",
            "training_end",
            "instructor_name",
            "final_score",
            "issued_at",
            "status",
            "pdf_path",
            "revoked_at",
            "revoked_reason",
        ]
        read_only_fields = [
            "id",
            "enrollment",
            "user",
            "course",
            "certificate_no",
            "verification_code",
            "issued_at",
            "revoked_at",
        ]


class IssueCertificateSerializer(serializers.Serializer):
    """Valida la entrada para emitir un certificado desde una matrícula."""

    enrollment_id = serializers.UUIDField()


class RevokeCertificateSerializer(serializers.Serializer):
    """Valida la anulación/revocación de un certificado."""

    revoked_reason = serializers.CharField(required=True, allow_blank=False, max_length=1000)


class PublicCertificateVerificationSerializer(serializers.ModelSerializer):
    """Proyección pública limitada para verificación externa."""

    class Meta:
        model = Certificate
        fields = [
            "certificate_no",
            "verification_code",
            "participant_name",
            "course_title",
            "hours",
            "modality",
            "training_start",
            "training_end",
            "instructor_name",
            "issued_at",
            "status",
        ]
class TestimonialSerializer(serializers.ModelSerializer):
    # Opcional: muestra el título del curso en respuestas GET (si tu modelo Course tiene campo 'title' o 'name')
    # course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "author_name",
            "author_role",
            "company",
            "content",
            "photo_url",
            "course",
            # "course_title",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
class ContactLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactLead
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "company",
            "interest",
            "message",
            "kind",
            "handled",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_email(self, value):
        if value:
            return value.strip().lower()
        return value

class SalesByMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesByMonth
        fields = ["month", "orders", "revenue"]
        read_only_fields = fields


class CourseStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStats
        fields = [
            "course_id",
            "title",
            "enrollments",
            "completed",
            "avg_progress",
            "certificates",
        ]
        read_only_fields = fields


class CompanyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyReport
        fields = [
            "company_id",
            "legal_name",
            "course_id",
            "course",
            "workers",
            "approved",
            "avg_progress",
        ]
        read_only_fields = fields

class CourseDetailSerializer(serializers.ModelSerializer):
    has_access = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "created_at",
            "has_access",
        ]

    def get_has_access(self, obj) -> bool:
        request = self.context.get("request")
        if not request or not request.user:
            return False
        return has_course_access(request.user, obj)

class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = [
            "id",
            "assessment",
            "enrollment",
            "user",
            "started_at",
            "submitted_at",
            "score",
            "passed",
        ]
        read_only_fields = [
            "id",
            "user",
            "started_at",
            "submitted_at",
            "score",
            "passed",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        enrollment = attrs.get("enrollment")

        # Validación opcional: asegurar que la matrícula pertenezca al usuario
        if enrollment and enrollment.user != user:
            raise serializers.ValidationError(
                {"enrollment": "Esta matrícula no pertenece al usuario autenticado."}
            )
        return attrs