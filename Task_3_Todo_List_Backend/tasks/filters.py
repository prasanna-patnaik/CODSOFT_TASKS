import django_filters

from tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    completed = django_filters.BooleanFilter(field_name="completed")
    priority = django_filters.ChoiceFilter(field_name="priority", choices=Task.Priority.choices)
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")

    class Meta:
        model = Task
        fields = ("completed", "priority", "category")
