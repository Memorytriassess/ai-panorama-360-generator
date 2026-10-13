# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.4.x   | yes       |
| 0.3.x   | security only |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@panorama360.local` with:

- A description of the issue and its impact.
- A minimal repro (prompt, config, model hash, OS, GPU driver).
- Whether it can be triggered without local file access.

Please do not open public issues for security reports. We aim to
acknowledge within 72 hours.

## Threat model

This tool loads local model checkpoints (`.safetensors`, `.ckpt`) and
optionally fetches model metadata over HTTPS. Relevant risks:

- **Untrusted checkpoints.** `torch.load` with `weights_only=False` is
  never used. All checkpoint loading goes through `safetensors` or
  `torch.load(..., weights_only=True)`. If you find a path that bypasses
  this, that is a vulnerability — report it.
- **Remote model metadata.** `services/registry_client.py` fetches JSON
  over HTTPS only, validates against the pydantic schema in
  `models/registry.py`, and never executes remote code.
- **Plugin processors.** Third-party processors are loaded from
  `~/.panorama360/plugins/` and run with full process privileges. Only
  install plugins you trust. We do not sandbox plugins.
- **Prompt injection via reference images.** EXIF and embedded text in
  reference images are stripped before they reach the prompt composer.

## Out of scope

- Denial of service from intentionally huge tile grids.
- Outputs that are aesthetically bad. That's a model problem, not a
  security problem.