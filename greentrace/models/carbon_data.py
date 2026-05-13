# greentrace/models/carbon_data.py
# UC-10: Input Carbon Data
# FR_24: Carbon Footprint Calculator
# FR_42: Violation alert when limit is exceeded

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .user import User
from .project import Project


class CarbonData(models.Model):
    """
    Monthly consumption data (fuel + electricity) for calculating
    the carbon footprint of a project.

    The calculate_co2() method applies international standard factors:
        1 L fuel        ~= 2.31  kg CO2
        1 kWh electricity ~= 0.233 kg CO2

    The (project, period_month, period_year) triplet is unique —
    a business can submit only one record per month.
    """

    project         = models.ForeignKey(
                          Project,
                          on_delete=models.CASCADE,
                          related_name="carbon_records"
                      )
    submitted_by    = models.ForeignKey(
                          User,
                          on_delete=models.PROTECT,
                          related_name="carbon_submissions"
                      )
    period_month    = models.PositiveSmallIntegerField(
                          validators=[MinValueValidator(1), MaxValueValidator(12)],
                          help_text="Reporting month (1-12)"
                      )
    period_year     = models.PositiveIntegerField(
                          help_text="Reporting year (e.g. 2025)"
                      )
    fuel_liters     = models.FloatField(
                          default=0.0,
                          help_text="Litres of fuel consumed during this month"
                      )
    electricity_kwh = models.FloatField(
                          default=0.0,
                          help_text="Kilowatt-hours of electricity consumed"
                      )
    total_co2_kg    = models.FloatField(
                          null=True, blank=True,
                          help_text="Total CO2 (kg) - calculated automatically"
                      )
    exceeds_limit   = models.BooleanField(
                          default=False,
                          help_text="True if project carbon limit is exceeded (FR_42)"
                      )
    created_at      = models.DateTimeField(auto_now_add=True)

    def calculate_co2(self) -> float:
        """
        Calculates and stores total_co2_kg based on international standards.
        Called before saving in save() or from a signal.
        """
        self.total_co2_kg = (
            self.fuel_liters      * 2.31
            + self.electricity_kwh * 0.233
        )
        return self.total_co2_kg

    def __str__(self):
        return (
            f"Carbon  {self.period_month:02d}/{self.period_year}"
            f"  -  {self.project.title}"
        )

    class Meta:
        verbose_name        = "Carbon Data"
        verbose_name_plural = "Carbon Data"
        unique_together     = ("project", "period_month", "period_year")
