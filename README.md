# vrslev/jack_server
Control [JACK Server](https://jackaudio.org/) with Python.

- Fully typed
- Can be used as replacement for [jackd](https://manpages.debian.org/buster/jackd2/jackd.1.en.html) for more robust configuration, for example, when using [`jack`](https://github.com/spatialaudio/jackclient-python) package 

📝 Project is in alpha stage.

## Installation

`
pip install jack_server
`

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
