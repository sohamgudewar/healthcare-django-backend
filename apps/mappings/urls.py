from django.urls import path
from .views import MappingListCreateView, PatientDoctorMappingDetailView

app_name = 'mappings'

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('<int:pk>/', PatientDoctorMappingDetailView.as_view(), name='mapping-detail'),
]
