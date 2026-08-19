"""Shared fixtures for the calfkit test suite.

Layout: `tests/` lives beside `src/` so tests exercise the INSTALLED package,
never the working copy. No __init__.py files anywhere under tests/ (pytest
runs with --import-mode=importlib). Lanes: unit/ is the default suite;
integration/ holds the opt-in marker lanes.
"""
