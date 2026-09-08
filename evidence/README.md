# Retained evidence is not application source

This directory includes immutable historical source snapshots, independent
evaluation harnesses, raw commands and reports. Some harnesses intentionally
retain their original local import paths and run with TypeScript type stripping;
they are not modules in the deployed application.

The application's TypeScript and lint checks exclude this archive. Product
source under `app/`, `components/` and `lib/`, and the portable current checks
under `scripts/`, remain checked. The exclusion does not turn an archived
harness into a passing application test: its own execution, environment, exit
status and independent review must support any claim based on it.

Keep historical bytes and failed attempts intact. Reproduction commands for a
released milestone are recorded in its evidence bundle and report; use those
commands rather than treating every archived script as a current entry point.
