from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import User, Course,Module,Lesson,StudentProgress


class UserResource(resources.ModelResource):
    # Map the 'author' foreign key using the author's name instead of their database ID
    is_student = fields.Field(
        column_name='is_student',
        attribute='is_student'
    )

    class Meta:
        model = User        
        import_id_fields = ('id',)
        # Skip rows that haven't changed
        skip_unchanged = True
        report_skipped = True