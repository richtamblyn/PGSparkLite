#####################################################################
# Spark Listener
#
# Run in a separate thread, posts to a callback url on value change
#
# Code originally written by paulhamsh.
# See https://github.com/paulhamsh/Spark-Parser
#####################################################################

from ast import literal_eval
from lib.common import dict_callback, dict_preset_corrupt, dict_connection_lost


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

                if self.reader.message[0][0] == 4:
                    #Acknowledgement
                    continue

                if self.reader.python is None:
                    continue

                self.notifier.raise_event(
                    dict_callback, data=literal_eval(self.reader.python))

            except AttributeError as att_err:
                print(att_err)
                self.notifier.raise_event(dict_preset_corrupt)
                break
            except Exception as err:
                print(err)
                self.notifier.raise_event(dict_connection_lost)
                break

    def stop(self):
        self.listening = False
