"""The opt-in integration lanes (ADR 0007): deselected by default, selected
by marker — `-m kafka` (real broker via testcontainers Redpanda; unused or
dynamic ports only, never hardcoded) and `-m live` (real model APIs;
main-only CI, never on PRs). Shared broker fixtures land here with the first
kafka test.
"""
