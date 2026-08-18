"""The default lane: broker-free, credential-free, no Docker.

Mirrors src/calfkit one test module per source module (test_<module>.py;
subpackages mirror as directories). Fakes come from the product —
calfkit.testing and calfkit.adapters.memory — never from test-local doubles.
"""
