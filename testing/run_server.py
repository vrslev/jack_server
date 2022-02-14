import time

from jack_server import Server, set_error_function, set_info_function

server = Server(
    driver="coreaudio", device="BuiltInSpeakerDevice", sync=True, period=1024
)
server.start()

time.sleep(0.5)

set_error_function(lambda s: None)
set_info_function(lambda s: None)
server.stop()
