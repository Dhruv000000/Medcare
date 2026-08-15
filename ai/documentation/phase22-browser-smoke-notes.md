# Phase 22 Browser Smoke Notes

The current Django API is running on `127.0.0.1:8000` with the disposable SQLite database. Ports `8001` and `8002` were already occupied by stale Django processes, so they were not used for the final smoke test. The existing static server on `127.0.0.1:8767` serves the current `/home/ubuntu/audit_project/medicare_phase2/frontend` tree. The login JavaScript defaults to `http://127.0.0.1:8000` for API calls.

The login page loaded successfully at `http://127.0.0.1:8767/pages/auth/login.html`, with role selectors for Patient, Doctor, and Admin, email/password fields, and a login button. The final smoke test will use the synthetic Phase 22 doctor and patient accounts seeded in the disposable SQLite database.

The doctor role selector and synthetic credentials filled correctly. Submitting the form did not redirect; the page displayed `Failed to fetch`. This is a smoke-test environment connectivity issue to diagnose before recording the final browser result. No real user credentials or data were used.

The final browser smoke origin is `http://127.0.0.1:8010`, which matches the development trusted-origin configuration. The Doctor role selected correctly, and the synthetic doctor credentials filled successfully. The form is ready for submission.

Authorized doctor smoke result: login succeeded from the allowed origin and redirected to `MediCare Doctor Dashboard`. The dashboard loaded the synthetic doctor identity, navigation, patient/schedule panels, and the Academic AI card. Clicking `Open Academic AI Tool` expanded the 13-feature form and displayed the academic/non-diagnostic disclaimer and doctor decision-boundary wording.

The authorized doctor form accepted the five numeric synthetic values (`55`, `130`, `240`, `150`, `1`) and the `sex=1` source code. Remaining categorical fields are being selected before submission.

The doctor form accepted `cp=3` and `fbs=0`; no client-side validation errors appeared. The remaining categorical codes are being entered next.

The form accepted `restecg=1` and `exang=0`; no client-side validation errors appeared. The final three categorical fields remain.

The form accepted `slope=2` and `ca=0`; no client-side validation errors appeared. Only `thal=3` remains before submitting the fixed synthetic vector.

Authorized doctor AI smoke result: submitting the complete fixed vector rendered `label_absent`, model probability `0.16164121253810007`, model `uci-heart-disease-logreg-v1.0.0`, status `academic_development_only`, the academic/non-diagnostic disclaimer, and the explicit doctor decision boundary. This matched the deterministic artifact check exactly.

Patient smoke setup result: the synthetic patient login succeeded and redirected to `MediCare | Patient Dashboard`. Patient navigation visibly includes `AI Health Insights`, along with the existing dashboard sections; no doctor-only AI form is exposed on this page.

Patient denial smoke result: the patient AI Health Insights page loaded with deferred educational content, no prediction form/result, and explicit text that no prediction request was sent. A direct synthetic request from the authenticated patient session to `/api/ai/heart-risk/predict/` returned HTTP `403` with `You do not have permission to perform this action.` The patient authorization boundary is preserved.
