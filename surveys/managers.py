from __future__ import absolute_import, unicode_literals

from django.db.models import QuerySet, Avg, Count


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


class QuestionResponseQuerySet(QuerySet):
    """
    Provides convenience methods to extract response stats.
    """

    def get_average(self):
        """
        If no rating data is present in the responses, None will be returned.
        """
        return self.aggregate(Avg("rating"))["rating__avg"]

    def get_frequencies(self, rating_choices):
        """
        Get rating frequencies for each rating in `rating_choices`.
        Choices that don't occur will still be included with a frequency of zero.
        """
        frequencies = dict(self.values_list("rating").annotate(Count("rating")))
        return [(choice, frequencies.get(choice, 0)) for choice in rating_choices]
