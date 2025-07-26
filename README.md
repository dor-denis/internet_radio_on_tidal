# Internet Radio to Tidal 🎶

This script listens to a radio stream (like Radio Arabella in the example), detects the current song, and adds it automatically to a Tidal playlist.

## 🔧 Requirements

- Python 3.9+
- ffprobe (from ffmpeg)
- A Tidal account

## ⚙️ Setup

```bash
git clone https://github.com/dor-denis/radio
cd internet_radio_to_tidal
python -m venv tidalenv
source tidalenv/bin/activate
pip install -r requirements.txt
```

## ⚙️ Configuration

You can configure the stream URL and list of "invalid" titles using a `config.yaml` file placed in the root folder.

### Example `config.yaml`:

```yaml
stream_url: "https://live.stream.radioarabella.de/radioarabella-muenchen/stream/mp3?aggregator=aramuc"

invalid_titles:
  - "Arabella München"
  - ""
  - "-"
  - "Radio Arabella - Mehr Musik, mehr Abwechslung"