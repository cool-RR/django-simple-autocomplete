import pickle
import hashlib

from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.conf import settings
from django.forms.fields import Field

_simple_autocomplete_queryset_cache = {}

from simple_autocomplete.widgets import AutoCompleteWidget, \
    AutoCompleteMultipleWidget


def ModelChoiceField__init__(self, queryset, empty_label=u"---------",
        cache_choices=False, required=True, widget=None, label=None,
        initial=None, help_text=None, to_field_name=None, *args, **kwargs):
    if required and (initial is not None):
        self.empty_label = None
    else:
        self.empty_label = empty_label
    self.cache_choices = cache_choices

    # Monkey starts here
    if self.__class__ in (ModelChoiceField, ModelMultipleChoiceField):
        meta = queryset.model._meta
        key = '%s.%s' % (meta.app_label, meta.module_name)
        # Handle both legacy settings SIMPLE_AUTOCOMPLETE_MODELS and new
        # setting SIMPLE_AUTOCOMPLETE.
        models = getattr(
            settings, 'SIMPLE_AUTOCOMPLETE_MODELS',
            getattr(settings, 'SIMPLE_AUTOCOMPLETE', {}).keys()
        )
        if key in models:
            pickled = pickle.dumps((
                queryset.model._meta.app_label,
                queryset.model._meta.module_name,
                queryset.query
            ))
            token = hashlib.md5(pickled).hexdigest()
            _simple_autocomplete_queryset_cache[token] = pickled
            if self.__class__ == ModelChoiceField:
                widget = AutoCompleteWidget(token=token, model=queryset.model)
            else:
                widget = AutoCompleteMultipleWidget(
                    token=token, model=queryset.model
                )
    # Monkey ends here

    # Call Field instead of ChoiceField __init__() because we don't need
    # ChoiceField.__init__().
    Field.__init__(self, required, widget, label, initial, help_text,
                   *args, **kwargs)

    self.queryset = queryset
    self.choice_cache = None
    self.to_field_name = to_field_name

ModelChoiceField.__init__ = ModelChoiceField__init__
