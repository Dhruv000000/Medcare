from apps.accounts.models import PatientProfile
from apps.medical_records.models import MedicalRecord
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.reports.models import MedicalReport

patient = PatientProfile.objects.get(user__email="phase26.smoke.patient@example.test")
print({
    "records": list(MedicalRecord.objects.filter(patient=patient).values_list("diagnosis", "doctor__user__email")),
    "reports": list(MedicalReport.objects.filter(patient=patient).values_list("title", "doctor__user__email")),
    "prescriptions": list(Prescription.objects.filter(patient=patient).values_list("status", "doctor__user__email")),
    "prescription_items": list(PrescriptionItem.objects.filter(prescription__patient=patient).values_list("medicine", "dosage", "frequency")),
})
