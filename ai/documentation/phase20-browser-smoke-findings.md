# Phase 20 Browser Smoke Findings

A disposable synthetic doctor account was created in the sandbox SQLite fallback only; no real patient data and no PostgreSQL were used.

The local login page was opened, the Doctor role was selected, and the synthetic doctor session authenticated successfully. The browser navigated to the existing Doctor Dashboard. The dashboard rendered the existing sidebar, header, cards, recent-patients panel, schedule panel, and navigation without patient records; the backend returned an empty authorized-patient list.

The existing AI card rendered in the established right-panel design slot with the title `Academic AI Risk Classification`, academic/development-only language, and the `Open Academic AI Tool` control. No AI request was sent before explicit user action. The model artifact was not exposed to the browser.

The doctor clicked `Open Academic AI Tool`, which expanded the existing AI card in place. The browser exposed all 13 labelled fields in the exact schema order and the form note stated that the backend remains authoritative and no identifiers/unrelated records should be entered. The safe synthetic values were filled successfully; no request was sent before the explicit submit action.

After explicit submission, the browser showed the submit button label `Analyzing…` while the request was in progress. The actual response rendered safely in the result region:

- Classification: `label_absent`
- Model probability: `0.16164121253810007`
- Model: `uci-heart-disease-logreg-v1.0.0`
- Status: `academic_development_only`
- Approved academic/non-clinical disclaimer displayed verbatim.

No raw JSON, stack trace, filesystem path, patient identifier, or model artifact was shown. The response was produced by the existing Phase 18 endpoint and unchanged Phase 17 artifact using synthetic academic values only.

For invalid-input smoke testing, age was changed to `100` and the doctor submitted the form. The browser displayed the controlled message `age must be between 29 and 77.` The existing result remained untouched and no additional API request was sent for the invalid client-side submission.
