# Phase 27 Synthetic Browser Smoke Notes

**Environment:** Disposable SQLite database, Django on `127.0.0.1:8001`, same-origin frontend/API proxy on `127.0.0.1:8000`. Synthetic accounts only.

## Patient workflow findings

The synthetic patient `phase26.smoke.patient@example.test` logged in through the real login page and was redirected to the patient dashboard. The dashboard loaded the synthetic appointment, profile summary, and quick-access cards.

The patient Medical Records page loaded the own-data clinical surface and displayed the existing empty state for the newly seeded patient. The patient Prescriptions page loaded the safe-DOM renderer and displayed the existing empty state with zero active/completed/refill-needed prescriptions. The patient Reports page loaded the own-data report surface and displayed the existing empty state with the protected upload/download controls present in the existing UI.

No real patient data was used. The remaining patient checks are AI denial, cross-patient isolation, and logout/session invalidation; doctor and Admin workflows remain to be checked in this browser run.

The patient AI Health Insights page rendered its limited-access/deferred state and explicitly stated that no prediction request was sent. A direct authenticated patient POST to `/api/ai/heart-risk/predict/` using the existing session wrapper returned HTTP `403`, confirming server-side patient AI denial.

The direct patient AI request returned `403`. The existing logout flow redirected to the login page, confirming the synthetic patient session was invalidated for the browser smoke path.

## Doctor workflow findings

The synthetic doctor `phase26.smoke.doctor@example.test` selected the Doctor role, logged in through the real login page, and was redirected to the doctor dashboard. The dashboard displayed one authorized synthetic patient, the appointment context, the existing academic AI card, and the existing authorized clinical-record modal entry point.

The doctor opened the existing Academic AI Tool. The form displayed the exact 13-feature schema, academic/non-diagnostic disclaimer, model-probability wording, and doctor decision responsibility. Synthetic numeric feature values were entered without patient identifiers; categorical fields remain to be selected before submission.

The doctor selected valid source-coded categorical values for `sex=1` and `cp=1` in the exact AI feature form. No patient identifier or clinical-record field was submitted.

The doctor submitted the exact 13-feature synthetic form through the real UI. The authorized AI response rendered `label_absent`, model probability `0.042370353583904195`, model `uci-heart-disease-logreg-v1.0.0`, status `academic_development_only`, the non-diagnostic disclaimer, doctor decision boundary, and all 13 native Logistic Regression feature contributions. No patient identifier was submitted.

The doctor opened Authorized Academic Reports and saw the newly created report scoped to that doctor, including the model version, probability-not-confidence wording, disclaimer, clinician responsibility statement, and 13 feature contributions. The doctor then opened the authorized patient’s appointment-scoped clinical modal; the appointment selector was populated and the Phase 26 create workflow panel exposed the record/report/prescription choices with server re-check messaging.

The doctor linked the clinical workflow to the authorized Feb 10, 2030 synthetic appointment and selected the Consultation record type. The modal continued to display the server re-check authorization message.

The doctor filled and submitted a synthetic consultation record for the authorized appointment. The UI submission completed through the existing Phase 26 handler; the modal remained in its controlled status/list state. Persistence and attribution will be confirmed by the read-only verification helper after the browser run.

The doctor switched to the report workflow and submitted a synthetic normal blood report with a structured normal finding, laboratory, summary, and interpretation. The real UI submission returned a visible report title in the refreshed modal, confirming the report creation path.

The prescription form was opened and a synthetic submission was attempted through the real UI handler. The first attempt did not show the medicine in the refreshed modal, so the controlled form status and selected appointment will be inspected before any retry; no application code will be changed.

The prescription submission diagnosis showed that switching workflow reset the appointment selector to no-link. The authorized appointment was then selected manually; all synthetic prescription fields remained populated and ready for a controlled retry.

The corrected prescription retry completed through the real UI handler with the authorized appointment selected. The refreshed modal still showed the report and controlled prescription form state but did not display the synthetic medicine, so the Phase 26 retained backend/browser evidence and a read-only persistence check will be used to distinguish UI refresh behavior from server persistence without modifying source code.

The read-only verifier initially showed the report and prescription persisted but no record from the first UI click. A controlled retry through the real record form handler then persisted `Phase 27 synthetic consultation retry`. Final read-only verification showed:

- record: `Phase 27 synthetic consultation retry`, owned by `phase26.smoke.doctor@example.test`;
- report: `Phase 27 synthetic blood report`, owned by `phase26.smoke.doctor@example.test`;
- prescription: active, owned by `phase26.smoke.doctor@example.test`;
- prescription item: `Phase 27 synthetic medicine`, `5 mg`, `Once daily`.

This was synthetic-only and server-owned. The first UI click did not persist a record; the controlled retry succeeded without source changes.

The synthetic doctor logout redirected to the login page through the existing logout flow, completing the doctor session-invalidation check.

## Admin workflow setup

The Admin role selector and login form loaded correctly, but the retained Phase 26 browser seed intentionally created only patient and doctor accounts. The synthetic Admin login therefore returned the controlled `Invalid email or password` state. A temporary disposable Admin-only seed script was created outside the project tree; no source or package file was changed.

The temporary disposable Admin fixture was corrected to use the existing `administrator` role constant and seeded successfully as `phase26.smoke.admin@example.test`. No application source or package file was changed.

## Admin workflow findings

After the disposable Admin fixture was seeded, the synthetic Admin logged in through the real login page and reached the Admin Dashboard. The dashboard displayed aggregate patient/doctor/appointment counts and recent appointments. The Patients page loaded and displayed both synthetic patient accounts with active status and existing administrative Deactivate controls.

The Admin Doctors page displayed both synthetic doctors, specialization, license, email, active status, and Deactivate controls. The Admin Appointments page displayed the two synthetic appointments with read-only lifecycle filters, dates, doctors, patients, statuses, and reasons.

The authenticated Admin browser session received HTTP `200` from the existing aggregate AI audit summary route and HTTP `403` for a direct POST to the doctor clinical-create route, confirming aggregate-only AI audit access and denial of detailed clinical writes. Admin logout redirected to the login page and completed session invalidation.
