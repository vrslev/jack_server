from jack_server import Server

master = Server(name="manager", driver="coreaudio", device="BuiltInSpeakerDevice")
master.start()
master.load_netmanager(ip="127.0.0.1")
input()
