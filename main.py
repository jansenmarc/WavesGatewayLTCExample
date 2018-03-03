"""
Litecoin Gateway
"""
import gevent.monkey
gevent.monkey.patch_all()

from waves_litecoin_gateway import LitecoinGateway

file = open("config.cfg", "r")

gateway = LitecoinGateway.from_config_file(file.read())

gateway.run()
