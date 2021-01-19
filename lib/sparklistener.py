#####################################################################
# Spark Listener
#
# Run in a separate thread, posts to a callback url on value change
#
# Code originally written by paulhamsh.
# See https://github.com/paulhamsh/Spark-Parser
#####################################################################

import requests

class SparkListener:

    def __init__(self, reader, comms, url):
        self._listening = True
        self._reader = reader
        self._comms = comms
        self._url = url

    def start(self):          

        self._listening = True

        while self._listening:
            try:
                dat = self._comms.get_data()            
                self._reader.set_message(dat)
                self._reader.read_message()                       
            
                if self._reader.python is None:
                    continue

                requests.post(self._url, json = self._reader.python)
            except AttributeError as att_err:
                print(att_err)
                requests.post(self._url, json = '{"PresetOneCorrupt": True}')
                break
            except Exception as err:
                print(err)
                requests.post(self._url, json = '{"ConnectionLost": True}')
                break        

    def stop(self):
        self._listening = False
        