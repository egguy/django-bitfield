from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import FieldListFilter
from django.contrib.admin.options import IncorrectLookupParameters

from bitfield import Bit


class BitFieldListFilter(FieldListFilter):
    """
    BitField list filter.
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = field_path
        self.lookup_val = int(request.GET.get(self.lookup_kwarg, 0))
        self.flags = field.flags
        self.labels = field.labels
        super(BitFieldListFilter, self).__init__(field,
            request, params, model, model_admin, field_path)

    def queryset(self, request, queryset):
        filter = dict((p, F(p) | v) for p, v in self.used_parameters.iteritems())
        try:
            return queryset.filter(**filter)
        except ValidationError, e:
            raise IncorrectLookupParameters(e)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        yield {
            'selected': self.lookup_val == 0,
            'query_string': cl.get_query_string({
                }, [self.lookup_kwarg]),
            'display': _('All'),
        }
        for number, flag in enumerate(self.flags):
            bit_mask = Bit(number).mask
            yield {
                'selected': self.lookup_val == bit_mask,
                'query_string': cl.get_query_string({
                        self.lookup_kwarg: bit_mask,
                    }),
                'display': self.labels[number],
            }
