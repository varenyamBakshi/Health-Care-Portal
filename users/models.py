from django.db import models
from django.contrib.auth.models import User
import os


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    open_time = models.TimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    close_time = models.TimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    speciality = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    slot_duration = models.TimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return self.user.username


DAY_CHOICES = (
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday")
)


class WorkingDays(models.Model):
    doctor = models.ForeignKey(
        Doctor, null=True, blank=True, on_delete=models.CASCADE)
    day_name = models.CharField(
        max_length=50, null=True, blank=True, choices=DAY_CHOICES, default='')

    def __str__(self):
        return self.day_name


class TimeSlots(models.Model):
    day = models.ForeignKey(WorkingDays, null=True,
                            blank=True, on_delete=models.CASCADE)
    start_time = models.TimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    end_time = models.TimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    occupied = models.BooleanField(default=False)

    def __str__(self):
        return self.day.doctor.user.username


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    time_slot = models.OneToOneField(
        TimeSlots, null=True, blank=True, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    alloted_time = models.TimeField(
        auto_now=False, null=True, blank=True, auto_now_add=False)
    meeting_link = models.URLField(max_length=200, blank=True)
    date_made = models.DateTimeField(auto_now_add=True)


class Medecine(models.Model):
    appointment = models.ForeignKey(
        Appointment, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    detail = models.CharField(max_length=100, blank=True, null=True)


# ------------------------------------------------------------------------------------
# pharmacy models

class Pharmacist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pharmacy', null=True, blank=True)
    phone = models.CharField(max_length=100, null=True)
    qualification = models.CharField(max_length=100, null=True)
    PharmaName = models.CharField(max_length=100, null=True)
    PharmaAddress = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.user.username


class specificproducts(models.Model):
    Pharmacist = models.ForeignKey(
        Pharmacist, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    price = models.FloatField()
    minquantity = models.IntegerField()
    available = models.IntegerField()
    cp = models.FloatField()
    quantity = models.CharField(max_length=100, null=True)
    drugs = models.CharField(max_length=200, null=True)
    brand = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

    def storename(self):
        return self.Pharmacist.PharmaName

    @property
    def profit(self):
        return (self.price-self.cp)


class allproducts(models.Model):
    name = models.CharField(max_length=100, null=True)
    image = models.ImageField(null=True, blank=True)
    price = models.FloatField()
    quantity = models.CharField(max_length=100, null=True)
    drugs = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(
        Patient, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    delivered = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def cartvalue(self):
        orderitems = self.cart_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.cart_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def shippingpossible(self):
        orderitems = self.cart_set.all()
        for i in orderitems:
            if i.quantity > i.product.available:
                return False
        return True


class Cart(models.Model):
    product = models.ForeignKey(
        specificproducts, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class WalkinOrder(models.Model):
    customer = models.ForeignKey(
        Pharmacist, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def cartvalue(self):
        orderitems = self.walkincart_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.walkincart_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def shippingpossible(self):
        orderitems = self.walkincart_set.all()
        for i in orderitems:
            if i.quantity > i.product.available:
                return False
        return True


class WalkinCart(models.Model):
    product = models.ForeignKey(
        specificproducts, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        WalkinOrder, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
# pharmacy models end
# -----------------------------------------------------------------------------------


# ------------------------------------------------------------
# new midels
SYMPTOM_CHOICES = (
    ("itching", "itching"),
    ("skin_rash", "skin_rash"),
    ("nodal_skin_eruptions", "nodal_skin_eruptions"),
    ("continuous_sneezing", "continuous_sneezing"),
    ("shivering", "shivering"),
    ("chills", "chills"),
    ("joint_pain", "joint_pain"),
    ("stomach_pain", "stomach_pain"),
    ("acidity", "acidity"),
    ("ulcers_on_tongue", "ulcers_on_tongue"),
    ("muscle_wasting vomiting", "muscle_wasting vomiting"),
    ("burning_micturition", "burning_micturition"),
    ("spotting_ urination", "spotting_ urination"),
    ("fatigue", "fatigue"),
    ("weight_gain", "weight_gain"),
    ("anxiety", "anxiety"),
    ("cold_hands_and_feets", "cold_hands_and_feets"),
    ("mood_swings", "mood_swings"),
    ("weight_loss", "weight_loss"),
    ("restlessness", "restlessness"),
    ("lethargy", "lethargy"),
    ("patches_in_throat", "patches_in_throat"),
    ("irregular_sugar_level", "irregular_sugar_level"),
    ("cough", "cough"),
    ("high_fever", "high_fever"),
    ("sunken_eyes", "sunken_eyes"),
    ("breathlessness", "breathlessness"),
    ("sweating", "sweating"),
    ("dehydration", "dehydration"),
    ("indigestion", "indigestion"),
    ("headache", "headache"),
    ("yellowish_skin", "yellowish_skin"),
    ("dark_urine", "dark_urine"),
    ("nausea", "nausea"),
    ("loss_of_appetite", "loss_of_appetite"),
    ("pain_behind_the_eyes", "pain_behind_the_eyes"),
    ("back_pain", "back_pain"),
    ("constipation", "constipation"),
    ("abdominal_pain", "abdominal_pain"),
    ("diarrhoea", "diarrhoea"),
    ("mild_fever", "mild_fever"),
    ("yellow_urine", "yellow_urine"),
    ("yellowing_of_eyes", "yellowing_of_eyes"),
    ("acute_liver_failure", "acute_liver_failure"),
    ("fluid_overload", "fluid_overload"),
    ("swelling_of_stomach", "swelling_of_stomach"),
    ("swelled_lymph_nodes", "swelled_lymph_nodes"),
    ("malaise", "malaise"),
    ("blurred_and_distorted_vision", "blurred_and_distorted_vision"),
    ("phlegm", "phlegm"),
    ("throat_irritation", "throat_irritation"),
    ("redness_of_eyes", "redness_of_eyes"),
    ("sinus_pressure", "sinus_pressure"),
    ("runny_nose", "runny_nose"),
    ("congestion", "congestion"),
    ("chest_pain", "chest_pain"),
    ("weakness_in_limbs", "weakness_in_limbs"),
    ("fast_heart_rate", "fast_heart_rate"),
    ("pain_during_bowel_movements", "pain_during_bowel_movements"),
    ("pain_in_anal_region", "pain_in_anal_region"),
    ("bloody_stool", "bloody_stool"),
    ("irritation_in_anus", "irritation_in_anus"),
    ("neck_pain", "neck_pain"),
    ("dizziness", "dizziness"),
    ("cramps", "cramps"),
    ("bruising", "bruising"),
    ("obesity", "obesity"),
    ("swollen_legs", "swollen_legs"),
    ("swollen_blood_vessels", "swollen_blood_vessels"),
    ("puffy_face_and_eyes", "puffy_face_and_eyes"),
    ("enlarged_thyroid", "enlarged_thyroid"),
    ("brittle_nails", "brittle_nails"),
    ("swollen_extremeties", "swollen_extremeties"),
    ("excessive_hunger", "excessive_hunger"),
    ("extra_marital_contacts", "extra_marital_contacts"),
    ("drying_and_tingling_lips", "drying_and_tingling_lips"),
    ("slurred_speech", "slurred_speech"),
    ("knee_pain", "knee_pain"),
    ("hip_joint_pain", "hip_joint_pain"),
    ("muscle_weakness", "muscle_weakness"),
    (" stiff_neck", " stiff_neck"),
    ("swelling_joints", "swelling_joints"),
    ("movement_stiffness", "movement_stiffness"),
    ("spinning_movements", "spinning_movements"),
    ("loss_of_balance", "loss_of_balance"),
    ("unsteadiness", "unsteadiness"),
    ("weakness_of_one_body_side", "weakness_of_one_body_side"),
    ("loss_of_smell", "loss_of_smell"),
    ("bladder_discomfort", "bladder_discomfort"),
    ("foul_smell_of urine", "foul_smell_of urine"),
    ("continuous_feel_of_urine", "continuous_feel_of_urine"),
    ("passage_of_gases", "passage_of_gases"),
    ("internal_itching", "internal_itching"),
    ("toxic_look_(typhos)", "toxic_look_(typhos)"),
    ("depression", "depression"),
    ("irritability", "irritability"),
    ("muscle_pain", "muscle_pain"),
    ("altered_sensorium", "altered_sensorium"),
    ("red_spots_over_body", "red_spots_over_body"),
    ("belly_pain", "belly_pain"),
    ("abnormal_menstruation", "abnormal_menstruation"),
    ("dischromic _patches", "dischromic _patches"),
    ("watering_from_eyes", "watering_from_eyes"),
    ("increased_appetite", "increased_appetite"),
    ("polyuria", "polyuria"),
    ("family_history", "family_history"),
    ("mucoid_sputum", "mucoid_sputum"),
    ("rusty_sputum", "rusty_sputum"),
    ("lack_of_concentration", "lack_of_concentration"),
    ("visual_disturbances", "visual_disturbances"),
    ("receiving_blood_transfusion", "receiving_blood_transfusion"),
    ("receiving_unsterile_injections", "receiving_unsterile_injections"),
    ("coma", "coma"),
    ("stomach_bleeding", "stomach_bleeding"),
    ("distention_of_abdomen", "distention_of_abdomen"),
    ("history_of_alcohol_consumption", "history_of_alcohol_consumption"),
    ("fluid_overload", "fluid_overload"),
    ("blood_in_sputum", "blood_in_sputum"),
    ("prominent_veins_on_calf", "prominent_veins_on_calf"),
    ("palpitations", "palpitations"),
    ("painful_walking", "painful_walking"),
    ("pus_filled_pimples", "pus_filled_pimples"),
    ("blackheads", "blackheads"),
    ("scurring", "scurring"),
    ("skin_peeling", "skin_peeling"),
    ("silver_like_dusting", "silver_like_dusting"),
    ("small_dents_in_nails", "small_dents_in_nails"),
    ("inflammatory_nails", "inflammatory_nails"),
    ("blister", "blister"),
    ("red_sore_around_nose", "red_sore_around_nose"),
    ("yellow_crust_ooze", "yellow_crust_ooze"),
)


class Symptom(models.Model):
    appointment = models.ForeignKey(
        Appointment, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=SYMPTOM_CHOICES, default='')


# ------------------------------------------------------------------------------------
# Pathologist models

class Pathologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=98, null=True)
    qualification = models.CharField(max_length=98, null=True)
    PathoName = models.CharField(max_length=100, null=True)
    PathoAddress = models.CharField(max_length=200, null=True)
    Pathoimage = models.ImageField(
        upload_to='pathology', null=True, blank=True)

    def __str__(self):
        return self.user.username


class labtest(models.Model):
    Pathologist = models.ForeignKey(
        Pathologist, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    price = models.FloatField()
    available = models.IntegerField()
    cp = models.FloatField()

    def __str__(self):
        return self.name

    def storename(self):
        return self.Pathologist.PathoName


class BookTest(models.Model):
    customer = models.ForeignKey(
        Patient, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    delivered = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def cartvalue(self):
        orderitems = self.tests_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_tests_items(self):
        orderitems = self.tests_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def shippingpossible(self):
        orderitems = self.tests_set.all()
        for i in orderitems:
            if i.quantity > i.product.available:
                return False
        return True


class Tests(models.Model):
    product = models.ForeignKey(labtest, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(
        BookTest, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class AnonyTests(models.Model):
    customer = models.ForeignKey(
        Pathologist, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def cartvalue(self):
        orderitems = self.addtests_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_tests_items(self):
        orderitems = self.addtests_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def shippingpossible(self):
        orderitems = self.addtests_set.all()
        for i in orderitems:
            if i.quantity > i.product.available:
                return False
        return True


class AddTests(models.Model):
    product = models.ForeignKey(
        labtest, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        AnonyTests, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
# Pathologist models end
# -----------------------------------------------------------------------------------
