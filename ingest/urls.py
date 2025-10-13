from django.urls import path
from . import views

urlpatterns = [
    path("wizard/", views.wizard, name="wizard"),
    path("wizard/submit/", views.wizard_submit, name="wizard_submit"),
]
