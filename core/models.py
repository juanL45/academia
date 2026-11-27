import uuid
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


# =====================================================================
# Utilidades
# =====================================================================
class PgEnumField(models.CharField):
    """CharField que apunta a un tipo ENUM nativo de PostgreSQL."""

    def __init__(self, *args, enum_name=None, **kwargs):
        self.enum_name = enum_name
        kwargs.setdefault("max_length", 30)
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return self.enum_name

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum_name"] = self.enum_name
        return name, path, args, kwargs


class UnmanagedBase(models.Model):
    class Meta:
        abstract = True
        managed = False


def uuid_pk():
    return models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


# =====================================================================
# Enums (TextChoices)
# =====================================================================
class UserRole(models.TextChoices):
    STUDENT = "student", "Alumno"
    INSTRUCTOR = "instructor", "Instructor"
    ADMIN = "admin", "Administrador"
    COMPANY_ADMIN = "company_admin", "Admin de empresa"


class CourseModality(models.TextChoices):
    VIRTUAL_SINCRONICA = "virtual_sincronica", "Virtual sincrónica"
    VIRTUAL_ASINCRONICA = "virtual_asincronica", "Virtual asincrónica"
    PRESENCIAL = "presencial", "Presencial"
    SEMIPRESENCIAL = "semipresencial", "Semipresencial"
    CORPORATIVO = "corporativo", "Corporativo"


class CourseLevel(models.TextChoices):
    BASICO = "basico", "Básico"
    INTERMEDIO = "intermedio", "Intermedio"
    AVANZADO = "avanzado", "Avanzado"


class PublishStatus(models.TextChoices):
    BORRADOR = "borrador", "Borrador"
    PUBLICADO = "publicado", "Publicado"
    ARCHIVADO = "archivado", "Archivado"


class LessonType(models.TextChoices):
    VIDEO = "video", "Video"
    PDF = "pdf", "PDF"
    LECTURA = "lectura", "Lectura"
    ENLACE = "enlace", "Enlace"
    EVALUACION = "evaluacion", "Evaluación"


class SessionPlatform(models.TextChoices):
    ZOOM = "zoom", "Zoom"
    GOOGLE_MEET = "google_meet", "Google Meet"
    PRESENCIAL = "presencial", "Presencial"
    OTRO = "otro", "Otro"


class AttendanceStatus(models.TextChoices):
    PRESENTE = "presente", "Presente"
    TARDANZA = "tardanza", "Tardanza"
    AUSENTE = "ausente", "Ausente"
    JUSTIFICADO = "justificado", "Justificado"


class EnrollmentStatus(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    ACTIVA = "activa", "Activa"
    COMPLETADA = "completada", "Completada"
    CANCELADA = "cancelada", "Cancelada"
    EXPIRADA = "expirada", "Expirada"


class OrderStatus(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    PAGADA = "pagada", "Pagada"
    FALLIDA = "fallida", "Fallida"
    REEMBOLSADA = "reembolsada", "Reembolsada"
    CANCELADA = "cancelada", "Cancelada"


class PaymentProvider(models.TextChoices):
    CULQI = "culqi", "Culqi"
    IZIPAY = "izipay", "Izipay"
    NIUBIZ = "niubiz", "Niubiz"
    MERCADOPAGO = "mercadopago", "Mercado Pago"
    YAPE_PLIN = "yape_plin", "Yape / Plin"
    TRANSFERENCIA = "transferencia", "Transferencia"
    EFECTIVO = "efectivo", "Efectivo"
    CORTESIA = "cortesia", "Cortesía"


class PaymentStatus(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    APROBADO = "aprobado", "Aprobado"
    RECHAZADO = "rechazado", "Rechazado"
    REEMBOLSADO = "reembolsado", "Reembolsado"


class DiscountType(models.TextChoices):
    PORCENTAJE = "porcentaje", "Porcentaje"
    MONTO_FIJO = "monto_fijo", "Monto fijo"


class QuestionType(models.TextChoices):
    OPCION_UNICA = "opcion_unica", "Opción única"
    OPCION_MULTIPLE = "opcion_multiple", "Opción múltiple"
    VERDADERO_FALSO = "verdadero_falso", "Verdadero / Falso"
    TEXTO_ABIERTO = "texto_abierto", "Texto abierto"


class CertificateStatus(models.TextChoices):
    VIGENTE = "vigente", "Vigente"
    REVOCADO = "revocado", "Revocado"


class CompanyRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    SUPERVISOR = "supervisor", "Supervisor"
    TRABAJADOR = "trabajador", "Trabajador"


# =====================================================================
# 2. Usuarios y sesiones
# =====================================================================
class UserManager(BaseUserManager):
    use_in_migrations = False

    def _create(self, email, password, **extra):
        if not email:
            raise ValueError("El correo es obligatorio")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)  # el backend guarda argon2/bcrypt en password_hash
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("role", UserRole.STUDENT)
        return self._create(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra["role"] = UserRole.ADMIN
        return self._create(email, password, **extra)


class User(AbstractBaseUser, UnmanagedBase):
    id = uuid_pk()
    email = models.TextField(unique=True)
    # AbstractBaseUser.password se guarda en la columna password_hash
    password = models.TextField(db_column="password_hash")
    last_login = models.DateTimeField(db_column="last_login_at", null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    first_name = models.TextField()
    last_name = models.TextField()
    document_type = models.TextField(default="DNI", null=True, blank=True)
    document_number = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    country = models.TextField(default="Perú", null=True, blank=True)
    region = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    profession = models.TextField(null=True, blank=True)
    employer = models.TextField(null=True, blank=True)
    avatar_url = models.TextField(null=True, blank=True)
    role = PgEnumField(enum_name="user_role", choices=UserRole.choices, default=UserRole.STUDENT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def get_all_permissions(self, obj=None):
        # Return a set of permission strings like {"app.add_model", "app.change_model"}
        return set()

    class Meta(UnmanagedBase.Meta):
        db_table = "users"
        constraints = [
            models.UniqueConstraint(
                fields=["document_type", "document_number"],
                condition=models.Q(document_number__isnull=False),
                name="uq_users_document",
            ),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    # Acceso al admin de Django sin PermissionsMixin (no hay tablas de permisos en el .sql)
    @property
    def is_staff(self):
        return self.is_active and self.role == UserRole.ADMIN

    @property
    def is_superuser(self):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff


class UserToken(UnmanagedBase):
    PURPOSES = [("verify_email", "Verificar correo"), ("reset_password", "Restablecer contraseña")]

    id = uuid_pk()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    purpose = models.TextField(choices=PURPOSES)
    token_hash = models.TextField(unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "user_tokens"


class UserSession(UnmanagedBase):
    id = uuid_pk()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    token_hash = models.TextField(unique=True)
    user_agent = models.TextField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "user_sessions"


# =====================================================================
# 3. Escuelas, docentes y cursos
# =====================================================================
class School(UnmanagedBase):
    id = uuid_pk()
    slug = models.TextField(unique=True)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    icon = models.TextField(null=True, blank=True)
    color = models.TextField(default="#24A7F3", null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "schools"
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class Instructor(UnmanagedBase):
    id = uuid_pk()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="instructor_profiles")
    full_name = models.TextField()
    headline = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo_url = models.TextField(null=True, blank=True)
    linkedin_url = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "instructors"

    def __str__(self):
        return self.full_name


class Course(UnmanagedBase):
    id = uuid_pk()
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="courses")
    slug = models.TextField(unique=True)
    title = models.TextField()
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    objectives = models.TextField(null=True, blank=True)
    target_audience = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    syllabus = models.JSONField(default=list, blank=True)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=1)
    modality = PgEnumField(enum_name="course_modality", choices=CourseModality.choices)
    level = PgEnumField(enum_name="course_level", choices=CourseLevel.choices,
                        default=CourseLevel.BASICO)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="PEN")
    thumbnail_url = models.TextField(null=True, blank=True)
    promo_video_url = models.TextField(null=True, blank=True)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    issues_certificate = models.BooleanField(default=True)
    access_days = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    status = PgEnumField(enum_name="publish_status", choices=PublishStatus.choices,
                         default=PublishStatus.BORRADOR)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    instructors = models.ManyToManyField(Instructor, through="CourseInstructor",
                                         related_name="courses")
    is_active = models.BooleanField(db_default=True)
    class Meta(UnmanagedBase.Meta):
        db_table = "courses"

    def __str__(self):
        return self.title


class CourseInstructor(UnmanagedBase):
    pk = models.CompositePrimaryKey("course", "instructor")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    is_lead = models.BooleanField(default=False)

    class Meta(UnmanagedBase.Meta):
        db_table = "course_instructors"


class CourseEdition(UnmanagedBase):
    id = uuid_pk()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="editions")
    name = models.TextField(null=True, blank=True)
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    status = PgEnumField(enum_name="publish_status", choices=PublishStatus.choices,
                         default=PublishStatus.PUBLICADO)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "course_editions"

    def __str__(self):
        return self.name or f"{self.course} ({self.starts_on})"


# =====================================================================
# 4. Contenido del aula virtual
# =====================================================================
class CourseModule(UnmanagedBase):
    id = uuid_pk()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta(UnmanagedBase.Meta):
        db_table = "course_modules"
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class Lesson(UnmanagedBase):
    id = uuid_pk()
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name="lessons")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.TextField()
    type = PgEnumField(enum_name="lesson_type", choices=LessonType.choices,
                       default=LessonType.VIDEO)
    video_provider = models.TextField(null=True, blank=True)
    video_ref = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    is_preview = models.BooleanField(default=False)
    is_required = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "lessons"
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class LessonResource(UnmanagedBase):
    id = uuid_pk()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    title = models.TextField()
    file_path = models.TextField()
    file_type = models.TextField(null=True, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "lesson_resources"


# =====================================================================
# 5. Clases en vivo
# =====================================================================
class LiveSession(UnmanagedBase):
    id = uuid_pk()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_sessions")
    edition = models.ForeignKey(CourseEdition, null=True, blank=True, on_delete=models.CASCADE,
                                related_name="live_sessions")
    instructor = models.ForeignKey(Instructor, null=True, blank=True, on_delete=models.PROTECT,
                                   related_name="live_sessions")
    title = models.TextField()
    platform = PgEnumField(enum_name="session_platform", choices=SessionPlatform.choices,
                           default=SessionPlatform.ZOOM)
    meeting_url = models.TextField(null=True, blank=True)
    meeting_code = models.TextField(null=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    recording_url = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "live_sessions"
        ordering = ["starts_at"]


# =====================================================================
# 6. Empresas (B2B)
# =====================================================================
class Company(UnmanagedBase):
    id = uuid_pk()
    ruc = models.CharField(max_length=11, unique=True, null=True, blank=True)
    legal_name = models.TextField()
    trade_name = models.TextField(null=True, blank=True)
    sector = models.TextField(null=True, blank=True)
    contact_name = models.TextField(null=True, blank=True)
    contact_email = models.TextField(null=True, blank=True)
    contact_phone = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    members = models.ManyToManyField(User, through="CompanyMember", related_name="companies")

    class Meta(UnmanagedBase.Meta):
        db_table = "companies"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.trade_name or self.legal_name


class CompanyMember(UnmanagedBase):
    pk = models.CompositePrimaryKey("company", "user")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = PgEnumField(enum_name="company_role", choices=CompanyRole.choices,
                       default=CompanyRole.TRABAJADOR)
    job_title = models.TextField(null=True, blank=True)
    area = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "company_members"


class CompanyProgram(UnmanagedBase):
    id = uuid_pk()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="programs")
    name = models.TextField()
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.TextField(default="activo")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "company_programs"

    def __str__(self):
        return self.name


class CompanyProgramCourse(UnmanagedBase):
    pk = models.CompositePrimaryKey("program", "course")
    program = models.ForeignKey(CompanyProgram, on_delete=models.CASCADE,
                                related_name="program_courses")
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    edition = models.ForeignKey(CourseEdition, null=True, blank=True, on_delete=models.PROTECT)
    seats = models.IntegerField(default=1)

    class Meta(UnmanagedBase.Meta):
        db_table = "company_program_courses"


# =====================================================================
# 7. Cupones, pedidos y pagos
# =====================================================================
class Coupon(UnmanagedBase):
    id = uuid_pk()
    code = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    type = PgEnumField(enum_name="discount_type", choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.PROTECT,
                               related_name="coupons")
    max_uses = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "coupons"

    def __str__(self):
        return self.code


class Order(UnmanagedBase):
    # order_number es "generated always as identity": no se mapea porque Django
    # intentaría escribirlo en cada save(). Léelo con .values("id") + SQL crudo
    # o cámbialo a "generated by default" si quieres exponerlo en el ORM.
    id = uuid_pk()
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.PROTECT,
                                related_name="orders")
    program = models.ForeignKey(CompanyProgram, null=True, blank=True, on_delete=models.PROTECT,
                                related_name="orders")
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.PROTECT,
                               related_name="orders")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="PEN")
    status = PgEnumField(enum_name="order_status", choices=OrderStatus.choices,
                         default=OrderStatus.PENDIENTE)
    billing_name = models.TextField(null=True, blank=True)
    billing_doc = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta(UnmanagedBase.Meta):
        db_table = "orders"

    # El trigger trg_order_paid crea las inscripciones al pasar a 'pagada'.
    def mark_paid(self):
        self.status = OrderStatus.PAGADA
        self.save(update_fields=["status"])


class OrderItem(UnmanagedBase):
    id = uuid_pk()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="order_items")
    edition = models.ForeignKey(CourseEdition, null=True, blank=True, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "order_items"


class Payment(UnmanagedBase):
    id = uuid_pk()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = PgEnumField(enum_name="payment_provider", choices=PaymentProvider.choices)
    provider_ref = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="PEN")
    status = PgEnumField(enum_name="payment_status", choices=PaymentStatus.choices,
                         default=PaymentStatus.PENDIENTE)
    receipt_url = models.TextField(null=True, blank=True)
    invoice_number = models.TextField(null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta(UnmanagedBase.Meta):
        db_table = "payments"


# =====================================================================
# 8. Inscripciones, progreso y asistencia
# =====================================================================
class Enrollment(UnmanagedBase):
    id = uuid_pk()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollments")
    edition = models.ForeignKey(CourseEdition, null=True, blank=True, on_delete=models.PROTECT,
                                related_name="enrollments")
    order_item = models.ForeignKey(OrderItem, null=True, blank=True, on_delete=models.PROTECT,
                                   related_name="enrollments")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.PROTECT,
                                related_name="enrollments")
    program = models.ForeignKey(CompanyProgram, null=True, blank=True, on_delete=models.PROTECT,
                                related_name="enrollments")
    status = PgEnumField(enum_name="enrollment_status", choices=EnrollmentStatus.choices,
                         default=EnrollmentStatus.PENDIENTE)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    enrolled_at = models.DateTimeField(default=timezone.now)
    access_until = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(UnmanagedBase.Meta):
        db_table = "enrollments"
        # En la BD el índice único usa coalesce(edition_id, uuid_nulo); no se replica aquí.

    def __str__(self):
        return f"{self.user} - {self.course}"

    @property
    def has_access(self):
        return (self.status in (EnrollmentStatus.ACTIVA, EnrollmentStatus.COMPLETADA)
                and (self.access_until is None or self.access_until > timezone.now()))


class LessonProgress(UnmanagedBase):
    # El trigger trg_progress recalcula Enrollment.progress_percent solo.
    pk = models.CompositePrimaryKey("enrollment", "lesson")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE,
                                   related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    last_position_secs = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "lesson_progress"


class SessionAttendance(UnmanagedBase):
    pk = models.CompositePrimaryKey("session", "enrollment")
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE,
                                related_name="attendance")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE,
                                   related_name="attendance")
    status = PgEnumField(enum_name="attendance_status", choices=AttendanceStatus.choices,
                         default=AttendanceStatus.AUSENTE)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT,
                                    related_name="+")

    class Meta(UnmanagedBase.Meta):
        db_table = "session_attendance"


# =====================================================================
# 9. Evaluaciones
# =====================================================================
class Assessment(UnmanagedBase):
    id = uuid_pk()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assessments")
    module = models.ForeignKey(CourseModule, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="assessments")
    title = models.TextField()
    instructions = models.TextField(null=True, blank=True)
    is_final = models.BooleanField(default=False)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_attempts = models.IntegerField(default=3)
    time_limit_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "assessments"

    def __str__(self):
        return self.title


class Question(UnmanagedBase):
    id = uuid_pk()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE,
                                   related_name="questions")
    type = PgEnumField(enum_name="question_type", choices=QuestionType.choices,
                       default=QuestionType.OPCION_UNICA)
    statement = models.TextField()
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    explanation = models.TextField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta(UnmanagedBase.Meta):
        db_table = "questions"
        ordering = ["sort_order"]


class QuestionOption(UnmanagedBase):
    id = uuid_pk()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.TextField()
    sort_order = models.IntegerField(default=0)

    class Meta(UnmanagedBase.Meta):
        db_table = "question_options"
        ordering = ["sort_order"]


class QuestionAnswerKey(UnmanagedBase):
    """Respuestas correctas. Nunca serializar esto hacia el alumno."""
    pk = models.CompositePrimaryKey("question", "option")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer_keys")
    option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, related_name="+")

    class Meta(UnmanagedBase.Meta):
        db_table = "question_answer_keys"


class Attempt(UnmanagedBase):
    id = uuid_pk()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE,
                                   related_name="attempts")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE,
                                   related_name="attempts")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="attempts")
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)

    class Meta(UnmanagedBase.Meta):
        db_table = "attempts"

    def grade(self):
        """Llama a grade_attempt() de PostgreSQL y refresca el objeto."""
        from django.db import connection
        with connection.cursor() as cur:
            cur.execute("select grade_attempt(%s)", [self.pk])
        self.refresh_from_db()
        return self


class AttemptAnswer(UnmanagedBase):
    pk = models.CompositePrimaryKey("attempt", "question")
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="+")
    option_ids = ArrayField(models.UUIDField(), default=list, blank=True)
    text_answer = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta(UnmanagedBase.Meta):
        db_table = "attempt_answers"


# =====================================================================
# 10. Certificados
# =====================================================================
class Certificate(UnmanagedBase):
    """
    certificate_no y verification_code los genera la BD (defaults con secuencia).
    Emite siempre con Certificate.issue(enrollment_id) en vez de crear a mano.
    """
    id = uuid_pk()
    enrollment = models.OneToOneField(Enrollment, on_delete=models.PROTECT,
                                      related_name="certificate")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="certificates")
    certificate_no = models.TextField(unique=True, editable=False)
    verification_code = models.TextField(unique=True, editable=False)
    participant_name = models.TextField()
    participant_doc = models.TextField(null=True, blank=True)
    course_title = models.TextField()
    hours = models.DecimalField(max_digits=6, decimal_places=1)
    modality = PgEnumField(enum_name="course_modality", choices=CourseModality.choices)
    training_start = models.DateField(null=True, blank=True)
    training_end = models.DateField(null=True, blank=True)
    instructor_name = models.TextField(null=True, blank=True)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    issued_at = models.DateTimeField(default=timezone.now)
    status = PgEnumField(enum_name="certificate_status", choices=CertificateStatus.choices,
                         default=CertificateStatus.VIGENTE)
    pdf_path = models.TextField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.TextField(null=True, blank=True)

    class Meta(UnmanagedBase.Meta):
        db_table = "certificates"

    def __str__(self):
        return self.certificate_no

    @classmethod
    def issue(cls, enrollment_id):
        """Ejecuta issue_certificate(); lanza excepción si no cumple requisitos."""
        return list(cls.objects.raw("select * from issue_certificate(%s)", [enrollment_id]))[0]

    @classmethod
    def verify(cls, code):
        """Equivalente a verify_certificate(): búsqueda pública por código o número."""
        code = code.strip().upper()
        return cls.objects.filter(
            models.Q(verification_code=code) | models.Q(certificate_no=code)
        ).only("certificate_no", "participant_name", "course_title", "hours", "modality",
               "training_start", "training_end", "instructor_name", "issued_at", "status"
               ).first()


# =====================================================================
# 11. Contenido web
# =====================================================================
class Testimonial(UnmanagedBase):
    id = uuid_pk()
    author_name = models.TextField()
    author_role = models.TextField(null=True, blank=True)
    company = models.TextField(null=True, blank=True)
    content = models.TextField()
    photo_url = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="testimonials")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "testimonials"


class ContactLead(UnmanagedBase):
    id = uuid_pk()
    full_name = models.TextField()
    email = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    company = models.TextField(null=True, blank=True)
    interest = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    kind = models.TextField(default="individual", null=True, blank=True)
    handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(UnmanagedBase.Meta):
        db_table = "contact_leads"


# =====================================================================
# 12. Vistas de reportes (solo lectura)
# =====================================================================
class ReadOnlyView(UnmanagedBase):
    class Meta:
        abstract = True
        managed = False

    def save(self, *args, **kwargs):
        raise NotImplementedError("Vista de solo lectura")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Vista de solo lectura")


class SalesByMonth(ReadOnlyView):
    month = models.DateTimeField(primary_key=True)
    orders = models.BigIntegerField()
    revenue = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta(ReadOnlyView.Meta):
        db_table = "v_sales_by_month"


class CourseStats(ReadOnlyView):
    course_id = models.UUIDField(primary_key=True)
    title = models.TextField()
    enrollments = models.BigIntegerField()
    completed = models.BigIntegerField()
    avg_progress = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    certificates = models.BigIntegerField()

    class Meta(ReadOnlyView.Meta):
        db_table = "v_course_stats"


class CompanyReport(ReadOnlyView):
    pk = models.CompositePrimaryKey("company_id", "course_id")
    company_id = models.UUIDField()
    legal_name = models.TextField()
    course_id = models.UUIDField()
    course = models.TextField()
    workers = models.BigIntegerField()
    approved = models.BigIntegerField()
    avg_progress = models.DecimalField(max_digits=5, decimal_places=1, null=True)

    class Meta(ReadOnlyView.Meta):
        db_table = "v_company_report"


# =====================================================================
# Autorización (equivalente a has_course_access() del .sql)
# =====================================================================
def has_course_access(user, course) -> bool:
    if not user.is_authenticated:
        return False
    if user.role == UserRole.ADMIN and user.is_active:
        return True
    now = timezone.now()
    if Enrollment.objects.filter(
        user=user, course=course,
        status__in=[EnrollmentStatus.ACTIVA, EnrollmentStatus.COMPLETADA],
    ).filter(models.Q(access_until__isnull=True) | models.Q(access_until__gt=now)).exists():
        return True
    return CourseInstructor.objects.filter(course=course, instructor__user=user).exists()