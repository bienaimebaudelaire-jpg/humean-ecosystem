# Legacy config migration note

This file is a historical reference from the legacy `humean-ai` prototype.

It is not used directly by the new `humean-ecosystem` repository.

## Why keep it

- it documents the original project assumptions;
- it shows the original runtime configuration shape;
- it helps migration work when bringing proven concepts into the new capability-based architecture.

## Migration shape

Old keys:
- `system.name` -> `name`
- `system.mode` -> `mode`
- `system.auto_update` -> `auto_update`
- `cognitive_engine.primary` -> `cognitive_engine.primary`
- `cognitive_engine.fallbacks` -> `cognitive_engine.fallbacks`
- `cognitive_engine.energy_threshold` -> `cognitive_engine.energy_threshold`
- `cognitive_engine.max_context_memories` -> `cognitive_engine.max_context_memories`
- `apis.*` -> moved to runtime environment variables if possible

## Important rule

The new architecture keeps the generic infrastructure public and the product-specific logic private. The legacy config belongs to the historical prototype layer, not the current public HUMEAN/OmniRoute core.
