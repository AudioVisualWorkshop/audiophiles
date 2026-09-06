# audiophiles
An audio-aware batch file renaming and organization tool designed for audio professionals

audiophiles is being designed specifically for audio professionals and will eventually support:

- Batch file renaming
- Audio-aware filename tokens
- Metadata-aware organization
- Technical audio properties
- Rename presets and workflows
- Preview and validation
- Safe filesystem operations
- Undo/history
- AI-assisted audio organization

## Development Status

audiophiles is currently in early development.

The initial development focus is the core rename engine. The GUI will be built on top of the core system once the underlying rename architecture is stable.

## Development

audiophiles requires Python 3.11 or newer.

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate