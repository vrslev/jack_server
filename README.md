[![Test](https://github.com/vrslev/jack_server/actions/workflows/test.yml/badge.svg)](https://github.com/vrslev/jack_server/actions/workflows/test.yml)

Control [JACK](https://jackaudio.org/) audio server with Python.
Can be used as replacement for [jackd](https://manpages.debian.org/buster/jackd2/jackd.1.en.html) for more robust configuration, for example, when using [`jack`](https://github.com/spatialaudio/jackclient-python) package.

## Installation

`pip install jack_server`

Also you need to have `jackserver` library on your machine, it comes with [JACK2](https://github.com/jackaudio/jack2). I had problems with apt-package on Ubuntu (`jackd2`), if you do too, compile jack yourself.

## Usage

### 🎛 `jack_server.Server`

On server creation you _can_ specify some parameters:

```python
import jack_server

server = jack_server.Server(
    name="myfancyserver",
    sync=True,
    realtime=False,
    driver="coreaudio",
    device="BuiltInSpeakerDevice",
    rate=48000,
    period=1024,
)
server.start()

input()
```

They are actually an equivalent of `jackd` flags:

- `-n`, `--name` to `name`,
- `-S`, `--sync` to `sync`,
- `-R`, `--realtime`, `-r`, `--no-realtime` to `realtime`,
- `-d` to `driver`,

And driver arguments:

- `-d`, `--device` to `device`,
- `-r`, `--rate` to `rate`,
- `-p`, `--period` to `period`,

#### `start(self) -> None`

_Open_ and _start_ the server. All state controlling methods are idempotent.

#### `stop(self) -> None`

Stop and close server.

#### `driver: jack_server.Driver`

Selected driver.

#### `name: str`

Actual server name. It is property that calls C code, so you can actually set the name.

#### `sync: bool`

Whether JACK runs in sync mode. Useful when you`re trying to send and receive multichannel audio.

#### `realtime: bool`

Whether JACK should start in realtime mode.

#### `params: dict[str, jack_server.Parameter]`

Server parameters mapped by name.

### 💼 `jack_server.Driver`

Driver (JACK backend), can be safely changed before server is started. Not supposed to be created by user code.

#### `name: str`

Driver name, read-only.

#### `device: str`

Selected device.

#### `rate: jack_server.SampleRate`

Sampling rate.

#### `period: int`

Buffer size.

#### `params: dict[str, jack_server.Parameter]`

Driver parameters mapped by name.

### 📻 `jack_server.SampleRate`

Valid sampling rate, `44100` or `48000`.

### 🔻 `jack_server.Parameter`

Not supposed to be created by user code.

#### `name: str`

Read-only verbose name of parameter.

#### `value: int | str | bytes | bool`

Value of the parameter, can be changed.

### ❗️ `jack_server.set_info_function(callback: Callable[[str], None] | None) -> None`

Set info output handler. By default JACK does is itself, i. e. output is being printed in stdout.

### ‼️ `jack_server.set_error_function(callback: Callable[[str], None] | None) -> None`

Set error output handler. By default JACK does is itself, i. e. output is being printed in stderr.
