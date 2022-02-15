# vrslev/jack_server

Control [JACK](https://jackaudio.org/) server with Python.
Can be used as replacement for [jackd](https://manpages.debian.org/buster/jackd2/jackd.1.en.html) for more robust configuration, for example, when using [`jack`](https://github.com/spatialaudio/jackclient-python) package.

## Installation

`pip install jack_server`

## Usage

### `jack_server.Server`

On server creation you _can_ specify some parameters:

```python
import jack_server

server = jack_server.Server(
    name="myfancyserver",
    driver="coreaudio",
    device="BuiltInSpeakerDevice",
    rate=48000,
    sync=True,
)
server.start()

input()
```

They are actually an equivalent of `jackd` flags:

- `-n`, `--name` to `name`,
- `-d` to `driver`,
- `-S`, `--sync` to `sync`

And driver arguments:

- `-d`, `--device` to `device`,
- `-r`, `--rate` to `rate`.

#### `start(self) -> None`

_Open_ and _start_ the server. All state controlling methods are idempotent.

#### `stop(self) -> None`

Stop and close server.

#### `driver: jack_server.Driver`

Selected driver.

#### `name: str`

Actual server name. It is property that calls C code, so you can actually set the name.

#### `sync: bool`

Wherther JACK runs in sync mode. Useful when you`re trying to send and receive multichannel audio.

#### `params: dict[str, jack_server.Parameter]`

Server parameters mapped by name.

### `jack_server.Driver`

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

### `jack_server.SampleRate`

Valid sampling rate, `44100` or `48000`.

### `jack_server.Parameter`

Not supposed to be created by user code.

#### `name: str`

Read-only verbose name of parameter.

#### `value: int | str | bytes | bool`

Value of the parameter, can be changed.

### `jack_server.set_info_function(callback: Callable[[str], None] | None) -> None`

Set info output handler. By default JACK does is itself, i. e. output is being printed in stdout.

### `set_error_function(callback: Callable[[str], None] | None) -> None`

Set error output handler. By default JACK does is itself, i. e. output is being printed in stderr.
