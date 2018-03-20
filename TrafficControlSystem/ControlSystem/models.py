from django.db import models
from django.contrib.auth.models import User, PermissionsMixin
from django.utils import timezone


class Inspector(User, PermissionsMixin):
    inspectorId = models.IntegerField(primary_key=True)

    def __str__(self):
        return "{}".format(self.username)


class Violation(models.Model):
    name = models.CharField(max_length=30,
                            null=False,
                            unique=True)
    fine = models.IntegerField(null=False)
    vehicleTaken = models.BooleanField(default=False)


class Location(models.Model):
    place = models.CharField(max_length=200)

    def __str__(self):
        return "{}".format(self.place)


class Challan(models.Model):
    issuedBy = models.ForeignKey(Inspector,
                                 on_delete=models.DO_NOTHING,
                                 related_name='issued_by')
    description = models.TextField()
    violations = models.ManyToManyField(Violation,
                                        through='ViolationToChallan')
    fine_collected = models.IntegerField()
    totalFine = models.IntegerField(default=0)
    timeOfIssue = models.DateTimeField(default=timezone.now)
    place = models.ForeignKey(Location,
                              on_delete=models.DO_NOTHING,
                              related_name='challan_issued_at')

    # vehicleRegistrationNumber

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        for violation in self.violations:
            self.totalFine += violation.fine
        super().save()


class ViolationToChallan(models.Model):
    challan = models.ForeignKey(Challan,
                                on_delete=models.DO_NOTHING)
    violation = models.ForeignKey(Violation,
                                  on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('challan', 'violation')


class Duty(models.Model):
    inspector = models.ForeignKey(Inspector,
                                  on_delete=models.DO_NOTHING,
                                  related_name='duties_done_by')
    place = models.ForeignKey(Location,
                              on_delete=models.DO_NOTHING,
                              related_name='duty_done_at')
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    challanIssued = models.IntegerField(default=0)

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        data_set = Challan.objects\
            .filter(Challan.place is self.place)\
            .filter(Challan.issuedBy is self.inspector)\
            .filter(Challan.timeOfIssue >= self.startTime and Challan.timeOfIssue <= self.endTime)
        self.challanIssued = len(data_set)
        super().save()

