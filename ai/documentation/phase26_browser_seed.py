from datetime import date, time

from apps.accounts.models import DoctorProfile, PatientProfile, User
from apps.appointments.models import Appointment

password = "Phase26-Smoke-Password-123!"

patient_user = User.objects.create_user(
    email="phase26.smoke.patient@example.test",
    password=password,
    first_name="Synthetic",
    last_name="Patient",
    role=User.Role.PATIENT,
)
patient = PatientProfile.objects.create(user=patient_user)
other_patient_user = User.objects.create_user(
    email="phase26.smoke.other.patient@example.test",
    password=password,
    first_name="Synthetic Other",
    last_name="Patient",
    role=User.Role.PATIENT,
)
other_patient = PatientProfile.objects.create(user=other_patient_user)
doctor_user = User.objects.create_user(
    email="phase26.smoke.doctor@example.test",
    password=password,
    first_name="Synthetic",
    last_name="Doctor",
    role=User.Role.DOCTOR,
)
doctor = DoctorProfile.objects.create(user=doctor_user, specialization="Cardiology", license_id="PH26-SMOKE-001")
other_doctor_user = User.objects.create_user(
    email="phase26.smoke.other.doctor@example.test",
    password=password,
    first_name="Synthetic Other",
    last_name="Doctor",
    role=User.Role.DOCTOR,
)
other_doctor = DoctorProfile.objects.create(user=other_doctor_user, specialization="Dermatology", license_id="PH26-SMOKE-002")
appointment = Appointment.objects.create(
    patient=patient,
    doctor=doctor,
    scheduled_date=date(2030, 2, 10),
    scheduled_time=time(9, 0),
    status=Appointment.Status.CONFIRMED,
    reason="Synthetic Phase 26 browser workflow",
)
Appointment.objects.create(
    patient=other_patient,
    doctor=other_doctor,
    scheduled_date=date(2030, 2, 11),
    scheduled_time=time(10, 0),
    status=Appointment.Status.CONFIRMED,
    reason="Synthetic unrelated appointment",
)
print({"password": password, "patient": patient_user.email, "doctor": doctor_user.email, "other_doctor": other_doctor_user.email, "appointment_id": appointment.pk, "patient_id": patient.pk})
