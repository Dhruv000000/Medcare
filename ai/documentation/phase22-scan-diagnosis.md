# Phase 22 Static Scan Diagnosis

The first static scan returned false positives that require scope refinement, not security-code changes.

- `frontend/js/patient/patient-ai-insights.js` uses `localStorage` only for the pre-existing theme and display-name preferences. It sends no prediction request, does not use `sessionStorage`, and renders the deferred AI notice with `textContent` and `replaceChildren`.
- `frontend/js/doctor/doctor-dashboard.js` contains pre-existing appointment/patient dashboard rendering with `insertAdjacentHTML` and `innerHTML`, but the Phase 20 AI workflow itself uses `replaceChildren`, `textContent`, and transient form state. The AI block does not persist inputs/results or access clinical records.
- The first artifact scan included `backend/venv`; source-tree artifact checks must exclude the vendored virtual environment and Python cache directories.

The scan script will be refined to target the AI-specific frontend block and source files only, while retaining route, checksum, dependency, secret, patient-denial, CSRF, and external-provider checks.
