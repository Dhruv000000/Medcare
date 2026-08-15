# Phase 21 Browser Smoke Findings

A disposable synthetic doctor account was used with the local SQLite fallback only. No real patient data and no PostgreSQL were used.

The existing login page rendered successfully. The Doctor role was selected and the existing session login form accepted the synthetic doctor credentials. The next smoke step is to submit the existing login and verify the refined doctor result experience.

The existing doctor login completed successfully. The dashboard rendered with the existing sidebar, header, navigation, patient summary, schedule, and the Academic AI Risk Classification card. No patient records were present in the synthetic smoke environment. No AI request occurred before explicit interaction.

The AI card opened in place and displayed the exact 13 labelled fields. The explanatory note visibly stated that model probability is an academic output rather than diagnostic confidence and that the doctor remains responsible for clinical interpretation and decisions. Synthetic academic values were filled without patient identifiers or unrelated clinical data.

After explicit submission, the browser showed `Analyzing…` and then rendered the actual response: classification `label_absent`, model probability `0.16164121253810007`, model `uci-heart-disease-logreg-v1.0.0`, and status `academic_development_only`. The approved disclaimer appeared, followed by the new message: `Doctor decision boundary: This is informational academic output. The doctor remains responsible for clinical interpretation and decision-making.` No diagnosis, treatment instruction, raw JSON, stack trace, patient data, or artifact path was displayed.
