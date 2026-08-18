"""Model-facing schema and request vocabulary: ToolSchema, ToolBinding,
ModelSettings, EngineRequest.

Flagged layout-v2 refinement (pending Ryan's OK): EngineRequest/ModelSettings
live HERE rather than models.py/providers.py — Provider.complete() is typed on
EngineRequest so it must sit below ports.py, and Model must stay httpx-free."""
