#####################################################################
# Spark Listener
#
# Run in a separate thread, posts to a callback url on value change
#
# Code originally written by paulhamsh.
# See https://github.com/paulhamsh/Spark-Parser
#####################################################################

from ast import literal_eval

class SparkListener:

    def __init__(self, reader, comms, notifier):
        self.listening = True
        self.reader = reader
        self.comms = comms
        self.notifier = notifier

    def start(self):          

        self.listening = True

        while self.listening:
            try:
                dat = self.comms.get_data()            
                self.reader.set_message(dat)
                self.reader.read_message()                       
            
                if self.reader.python is None:
                    continue
                
                self.notifier.raise_event("callback", data=literal_eval(self.reader.python))
                
            except AttributeError as att_err:
                print(att_err)
                self.notifier.raise_event("preset_corrupt")
                break
            except Exception as err:
                print(err)
                self.notifier.raise_event("connection_lost")                
                break        

    def stop(self):
        self._listening = False
        