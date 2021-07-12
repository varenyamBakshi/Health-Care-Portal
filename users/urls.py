from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('doctor/dashboard/', views.doctorDashboard, name='doctorDashboard'),
    path('patient/dashboard/', views.patientDashboard, name='patientDashboard'),
    path('patient/dashboard/appointments/',
         views.patientAppointments, name='patientAppointments'),
    path('patient/bookAppointment/<int:pk>/<str:pk2>/<str:pk3>/',
         views.bookAppointment, name='bookAppointment'),
    path('doctor/dashboard/appointments/',
         views.doctorAppointments, name='doctorAppointments'),
    path('doctor/dashboard/appointments/<int:pk>/',
         views.appointmentMedsdoc, name='appointmentMedsdoc'),
    path('patient/dashboard/appointments/<int:pk>/',
         views.appointmentMeds, name='appointmentMeds'),
    path('doctor/dashboard/appointments/update/<int:pk>/',
         views.updateAppointment, name='updateAppointment'),
    path('doctor/dashboard/appointments/meds/update/<int:pk>/',
         views.updateAppointmentMeds, name='updateAppointmentMeds'),
    path('doctor/profile/update', views.doctorProfileUpdate,
         name='doctorProfileUpdate'),
    path('patient/profile/update', views.patientProfileUpdate,
         name='patientProfileUpdate'),
    #     path('pharmacist/dashboard/', views.pharmacistDashboard,
    #          name='pharmacistDashboard'),
    path('pathologist/dashboard/', views.pathologistDashboard,
         name='pathologistDashboard'),



    # ------------------------------------------------------------------------------------------------------
    # all the pharmacy urls here
    path('pharmacist/dashboard/', views.pharmacistDashboard,
         name='pharmacistDashboard'),
    path('pharmacy/', views.pharmacy, name='pharmacy'),
    path('pharmacy/cart/', views.cart, name='cart'),
    path('walkin/cart/', views.walkincart, name='walkincart'),
    path('pharmacy/checkout/', views.customercheckout, name='checkout'),
    path('pharmacy/<int:pharmacyid>/', views.store, name='store'),
    path('pharmacy/update_item/', views.updateitem, name="update_item"),
    path('pharmacy/update_item_walkin/',
         views.updateitemwalkin, name="update_item_walkin"),
    path('pharmacist/stock/', views.stock, name='stock'),
    path('pharmacist/deleteproduct/', views.deleteproduct, name='deleteproduct'),
    path('pharmacist/addproduct/', views.addproduct, name='addproduct'),
    path('pharmacist/alertproducts/', views.alertproducts, name='alertproducts'),
    path('pharmacy/placeorder/', views.placeonlineorder, name='placeonlineorder'),
    path('pharmacist/placeorder/', views.placeofflineorder,
         name='placeofflineorder'),
    path('pharmacist/onlineorders/', views.onlineorders, name='onlineorders'),
    path('pharmacist/onlineorderscomplete/',
         views.onlineorderscomplete, name='onlineorderscomplete'),
    path('pharmacist/walkinorders/', views.offlineorders, name='offlineorders'),
    path('pharmacy/ordersuccess/', views.ordersuccess, name='ordersuccess'),
    path('pharmacist/deliverorder/', views.deliverorder, name='deliverorder'),
    path('pharmacy/myorders/', views.myorders, name='myorders'),
    # pharmacy urls end
    # ------------------------------------------------------------------------------------------------------

    path('signup/', views.signupUser, name='signupUser'),
    path('login/', views.loginUser, name='loginUser'),
    path('logout/', views.logoutUser, name='logoutUser'),


    # ------------------------
    # new imports
    path('patient/dashboard/appointments/<int:pk>/symptoms/',
         views.appointmentSymptoms, name='appointmentSymptoms'),
    path('patient/dashboard/appointments/<int:pk>/symptoms/update/',
         views.updateAppointmentSymptoms, name='updateAppointmentSymptoms'),
    path('patient/dashboard/appointments/<int:pk>/guessDisease/',
         views.guessDisease, name='guessDisease'),
    path('patient/myprescriptions/',
         views.myprescriptions, name='myprescriptions',),
    path('pinandbuy/<int:pid>/pharmacy',
         views.pinandbuypharmacy, name='pinandbuypharmacy'),
    path('pinandbuy/pharmacy/<int:pharmacyid>/<int:pid>',
         views.pinandbuystore, name='pinandbuystore'),



    # ------------------------------------------------------------------------------------------------------
    # all the pathology urls here
    path('pathologist/dashboard/', views.pathologistDashboard,
         name='pathologistDashboard'),
    path('pathology/', views.pathology, name='pathology'),
    path('pathology/tests/', views.tests, name='tests'),
    path('pathology/walkin/tests/', views.addtests, name='addtests'),
    path('pathology/outcheck/', views.outcheck, name='outcheck'),
    path('pathology/<int:pathologyid>/', views.dukan, name='dukan'),
    path('pathology/update_item/', views.itemupdating, name="update_item"),
    path('pathology/update_item_walkin/',
         views.itemupdatedwalkin, name="update_item_walkin"),
    path('pathologist/market/', views.market, name='market'),
    path('pathologist/removeproduct/', views.removeproduct, name='removeproduct'),
    path('pathologist/testsadd/', views.testsadd, name='testsadd'),
    path('pathologist/alarmtests/', views.alarmtests, name='alarmtests'),
    path('pathology/placeorder/', views.flipkart, name='flipkart'),
    path('pathologist/placeorder/', views.amazon, name='amazon'),
    path('pathologist/orderonline/', views.orderonline, name='orderonline'),
    path('pathologist/completedorder/',
         views.completedorder, name='completedorder'),
    path('pathologist/walkinorders/', views.orderoffline, name='orderoffline'),
    path('pathology/successorder/', views.successorder, name='successorder'),
    path('pathologist/ekart/', views.ekart, name='ekart'),
    path('pathalogy/itsmychoice/', views.itsmychoice, name='itsmychoice'),
    # pathology urls end
    # ------------------------------------------------------------------------------------------------------


    # video calling urls
    # --------------------------------------------------

    path('videocall/<int:meetingid>/', views.videocall, name="videocall"),


    # video calling urls end
    # -----------------------------------------------



]
