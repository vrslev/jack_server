# Control JACK Server with Python

📝 Project is in alpha stage.

## Installation

```bash
pip install jack_server
```

## Usage

```python
import jack_server

server = jack_server.Server(
    driver="coreaudio",
    device="BuiltInSpeakerDevice",
    rate=48000,
    sync=True,
)
server.start()

input()
```
