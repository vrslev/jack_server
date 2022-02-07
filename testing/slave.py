from jack_server import Server

slave = Server(name="slave", driver="coreaudio", device="BlackHole16ch_UID")
slave.start()
slave.load_netadapter(ip="127.0.0.1")
input()
