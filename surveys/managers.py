from __future__ import absolute_import, unicode_literals

from django.db.models import QuerySet


class RatingDataQuerySet(QuerySet):
    """
    Provides convenience methods for models that retrieve rating data.
    """

    def get_rating_data(self, purchase):
        """
        Generate rating data for all instances in the queryset.
        Instances that return None will be skipped.
        """
        nodes = (instance.get_rating_data(purchase) for instance in self)
        return list(n for n in nodes if n is not None)
