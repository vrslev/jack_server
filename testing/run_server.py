import time

import jack_server

server = jack_server.Server(
    driver="coreaudio",
    device="BuiltInSpeakerDevice",
    period=1024,
    sync=True,
)
server.start()

time.sleep(0.5)

jack_server.set_error_function(None)
jack_server.set_info_function(None)
server.stop()
