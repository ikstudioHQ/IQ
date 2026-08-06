# ERROR RECOVERY — Error Recovery Procedures

## Purpose
Defines recovery procedures for all possible failure types.

## Failure Types & Recovery

### Missing Files
- Check workspace directory.
- Confirm file exists in repository.
- Load from backup if available.
- Log error in `generation_log.json`.
- Stop pipeline. Do not continue without required files.

### Invalid JSON
- Validate against schema.
- Confirm syntax.
- Repair or regenerate from known source.
- Confirm version consistency.
- Log repair in `generation_log.json`.

### Broken YAML
- Validate syntax.
- Confirm structure matches `settings.yaml` schema.
- Repair or regenerate.
- Confirm all required keys present.

### Duplicate Topics
- Load `available_topics.json` and `completed_topics.json`.
- Confirm new topic is unique.
- If duplicate found, select next available topic or create new one.
- Confirm curriculum prerequisites met.
- Log selection in `generation_log.json`.

### Missing Assets
- Confirm asset exists in `asset_registry.json`.
- Confirm file exists in workspace.
- Generate new asset or load alternative.
- Confirm brand consistency.

### Missing Characters
- Confirm character exists in `knowledge_characters.json`.
- Confirm active status in `active_characters.json`.
- Load character profile or select alternative.
- Confirm personality consistency.

### Failed Generation
- Confirm prompt loaded correctly.
- Confirm model available.
- Confirm temperature and settings correct.
- Retry with same or adjusted settings.
- Log attempt in `generation_log.json`.

### Incomplete Package
- Confirm all required files present.
- Confirm ZIP integrity.
- Confirm database updates completed.
- Confirm quality checks passed.
- Do not publish incomplete packages.

### Local File Conflicts
- Confirm local file version consistency.
- Confirm latest local file version.
- Resolve conflicts manually with clear rules.
- Confirm final consistency.

### Validation Failures
- Confirm which validation failed.
- Confirm which rules broken.
- Return to appropriate pipeline step.
- Repair or regenerate.
- Confirm repair passes validation.
- Log repair.

## Related Files
`MASTER.md`, `MEMORY.md`, `WORKFLOW.md`
