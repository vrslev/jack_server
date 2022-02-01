# Control JACK Server with Python

📝 Project is in alpha stage.

## Installation

```bash
pip install jack_server
```

## Usage

```python
import time

from jack_server import Server

server = Server(
    driver="coreaudio",
    device="BuiltInSpeakerDevice",
    rate=48000,
    sync=True,
)
server.start()

while True:
    time.sleep(1)
```
