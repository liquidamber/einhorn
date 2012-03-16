from django.db import models
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

MAX_KILO_DIGITS = 6
MAX_TRAIN_ID_LENGTH = 16
MAX_TRAIN_CLASS_NAME_LENGTH = 32
MAX_TRAIN_CLASS_TYPE_LENGTH = 32
MAX_SHEET_CLASS_NAME_LENGTH = 32


class EinhornProfile(models.Model):
    profile_url = models.URLField(_("URL for profile page"),
                                  blank=True)
    private = models.BooleanField(_("private flag"))
    default_accept = models.BooleanField(_("default accept policy flag"))
    accept_users = models.ManyToManyField(auth.models.User,
                                          blank=True,
                                          related_name='accept_users')
    deny_users = models.ManyToManyField(auth.models.User,
                                        blank=True,
                                        related_name='deny_users')
    total_kilo = models.DecimalField(_("total sum of kilo, only cache"),
                                     max_digits=MAX_KILO_DIGITS,
                                     decimal_places=1,
                                     blank=True, null=True, editable=False)
    unique_kilo = models.DecimalField(_("unique sum of kilo, only cache"),
                                      max_digits=MAX_KILO_DIGITS,
                                      decimal_places=1,
                                      blank=True, null=True, editable=False)


class SheetClass(models.Model):

    """
    Specify the class of the sheet.
    """

    name = models.CharField(_("name of the sheet class"),
                            max_length=MAX_SHEET_CLASS_NAME_LENGTH)
    company = models.ManyToManyField('django_traindb.Company')


BASIC_TYPE_CHOICES = (
    ('HSR', _("high-speed railway express")),
    ('LTD', _("limited express")),
    ('EXP', _("express (with special fee)")),
    ('RPD', _("rapid (without special fee)")),
    ('LOC', _("local")),
    )


class TrainClass(models.Model):

    """
    Train class, such as "Orient Express" or "Nozomi express" and so on.
    """

    basic_type = models.CharField(_("basic train type"),
                                  choices=BASIC_TYPE_CHOICES, max_length=3)
    specific_type = models.CharField(_("company specific train type"),
                                     max_length=MAX_TRAIN_CLASS_TYPE_LENGTH)
    # render_color = models.IntegerField(_("rendering color"),
    #                                    null=True, blank=True)
    name = models.CharField(_("train name"),
                            max_length=MAX_TRAIN_CLASS_NAME_LENGTH,
                            blank=True)
    classes = models.ManyToManyField(SheetClass,
                                     help_text=_("The classes to constitute the train"))
    company = models.ManyToManyField('django_traindb.Company')


class TrainDia(models.Model):

    """
    Train dia in time table, such as "Nozomi Express #301" or so on.
    """

    train_class = models.ForeignKey(TrainClass)
    train_id = models.CharField(_("train identifier"),
                                max_length=MAX_TRAIN_ID_LENGTH)
    is_up = models.BooleanField(_("up train flag"),
                                help_text=_("True if the train is up."))
    rivised_date = models.DateField(_("date when the dia is revised"))


class Segment(models.Model):

    """segment between two station with the same line."""

    start_station = models.ForeignKey('django_traindb.Station',
                                      related_name='%(class)s_start_station')
    end_station = models.ForeignKey('django_traindb.Station',
                                    related_name='%(class)s_end_station')

    class Meta:
        abstract = True


class TrainDiaSegment(Segment):

    """
    Train dia segment, which tells train stopping segment.
    """

    traindia = models.ForeignKey(TrainDia)
    start_day = models.IntegerField(_("days of starting from start station"))
    end_day = models.IntegerField(_("days of arriving at end station"))
    start_time = models.DateField(_("start time of the log"),
                                  blank=True, null=True)
    end_time = models.DateField(_("end time of the log"),
                                blank=True, null=True)


class TripLog(models.Model):

    """Riding log in terms of trip."""

    owner = models.ForeignKey(auth.models.User,
                              related_name='owner_triplog')
    partners = models.ManyToManyField(auth.models.User,
                                      blank=True,
                                      related_name='partner_triplog')
    memo = models.TextField(_("memo of the trip"),
                            blank=True)
    start_date = models.DateField(_("start date of the trip, only a cache"),
                                  blank=True, null=True, editable=False)
    end_date = models.DateField(_("end date of the trip, only a cache"),
                                blank=True, null=True, editable=False)


class TrainLog(models.Model):

    """Riding log in terms of one train."""

    triplog = models.ForeignKey(TripLog)
    train = models.ForeignKey(TrainDia)
    sheet = models.ForeignKey(SheetClass)
    start_date = models.DateField(_("start date of the log"),
                                  blank=True, null=True)
    end_date = models.DateField(_("end date of the log"),
                                blank=True, null=True)
    # OnSave and OnDelete, we have to maintain trip date.


class SegmentLog(Segment):

    """Riding log in terms of one line segment."""

    trainlog = models.ForeignKey(TrainLog)
    line = models.ForeignKey('django_traindb.Line')
    memo = models.TextField(_("memo of the log"), blank=True)
