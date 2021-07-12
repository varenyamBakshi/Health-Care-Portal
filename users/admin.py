from django.contrib import admin
from .models import *

admin.site.register(Doctor)
admin.site.register(WorkingDays)
admin.site.register(TimeSlots)
admin.site.register(Patient)
admin.site.register(Pharmacist)
admin.site.register(Pathologist)
admin.site.register(Appointment)
admin.site.register(Medecine)


# ----------------------------------------------------
# pharmacy registrations
admin.site.register(specificproducts)
admin.site.register(allproducts)
# admin.site.register(Pharmacist)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(WalkinOrder)
admin.site.register(WalkinCart)
# pharmacy Registration over
# ----------------------------------------------------


# ----------------------------------------------------
# pathology registrations
admin.site.register(labtest)

admin.site.register(BookTest)
admin.site.register(Tests)
admin.site.register(AnonyTests)
admin.site.register(AddTests)

# pathology Registration over
# ----------------------------------------------------
