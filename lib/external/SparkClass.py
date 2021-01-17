########
#
# Spark Class
#
# Class to package commands to send to Positive Grid Spark
#
# See https://github.com/paulhamsh/Spark-Parser


import struct


class SparkMessage:
    def __init__(self):
       
        # declarations
        self.data = b''
        self.split_data8=[]
        self.split_data7=[]
        self.final_data=[]
        self.cmd=0
        self.sub_cmd=0

    ######## Helper functions to package a command for the Spark (handles the 'format bytes'

        
    # Start the process - clear the data and create the headers
    def start_message (self, cmd, sub_cmd, multi = False):
        self.cmd = cmd
        self.sub_cmd = sub_cmd
        self.multi = multi
        self.data=b''
        self.split_data8=[]
        self.split_data7=[]
        self.final_message=[]

    def end_message(self):

        # determine how many chunks there are

        data_len = len (self.data)
        
        num_chunks = int ((data_len + 0x7f) / 0x80 )
      
        # split the data into chunks of maximum 0x80 bytes (still 8 bit bytes)
        # and add a chunk sub-header if a multi-chunk message
        

        for this_chunk in range (0, num_chunks):
            chunk_len = min (0x80, data_len - (this_chunk * 0x80))
            if (num_chunks > 1):
                # we need the chunk sub-header
                data8 = bytes([num_chunks]) + bytes([this_chunk]) + bytes([chunk_len])
            else:
                data8 = b''
            data8 += self.data[this_chunk * 0x80 : this_chunk * 0x80 + chunk_len]

            self.split_data8.append (data8)
          
        # now we can convert this to 7-bit data format with the 8-bits byte at the front
        # so loop over each chunk
        # and in each chunk loop over every sequence of (max) 7 bytes
        # and extract the 8th bit and put in 'bit8'
        # and then add bit8 and the 7-bit sequence to data7

        for chunk in self.split_data8:

            chunk_len = len (chunk)
            num_seq = int ((chunk_len + 6) / 7)
            bytes7 = b''
            
            for this_seq in range (0, num_seq):
                seq_len = min (7, chunk_len - (this_seq * 7))
                bit8 = 0
                seq = b''
                for ind in range (0,seq_len):
                    # can change this so not [dat] and not [ x: x+1]
                    dat = chunk[this_seq * 7 + ind]
                    if dat & 0x80 == 0x80:
                        bit8 |= (1<<ind)
                    dat &= 0x7f
                    seq +=  bytes([dat])
                bytes7 += bytes([bit8]) + seq
                
            self.split_data7.append(bytes7)   

        # now we can create the final message with the message header and the chunk header
        block_header = b'\x01\xfe\x00\x00\x53\xfe'
        block_filler = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        chunk_header = b'\xf0\x01\x3a\x15'
        
        for chunk in self.split_data7:
            block_size = len (chunk) + 16 + 6 + 1
            header = (block_header + bytes([block_size]) +
                    block_filler + chunk_header +
                    bytes([self.cmd]) + bytes([self.sub_cmd]) )
            trailer = b'\xf7'
            self.final_message.append(header + chunk + trailer)

        return self.final_message

    def add_bytes(self, bytes_8):
        self.data += bytes_8


    ######## Helper functions for packing data types

    def add_prefixed_string(self, pack_str):
        self.add_bytes (bytes([len(pack_str)]))
        self.add_bytes (bytes([len(pack_str) + 0xa0]) + bytes(pack_str, 'utf-8'))

    def add_string(self, pack_str):
        self.add_bytes (bytes([len(pack_str) + 0xa0]) + bytes(pack_str, 'utf-8'))

    def add_long_string(self, pack_str):
        self.add_bytes (b'\xd9')
        self.add_bytes (bytes([len(pack_str)]) + bytes(pack_str, 'utf-8'))    

    # floats are special - bit 7 is actually stored in the format byte and not in the data
    def add_float (self, flt):
        bytes_val = struct.pack(">f", flt)
        self.add_bytes(b'\xca')
        self.add_bytes(bytes_val)

           
    def add_onoff (self, onoff):
        if onoff == "On":
            b = b'\xc3'
        else:
            b = b'\xc2'
        self.add_bytes(b)
    
    ######## Functions to package a command for the Spark


    def change_effect_parameter (self, pedal, param, val):
        cmd = 0x01
        sub_cmd = 0x04
    
        self.start_message (cmd, sub_cmd)
        self.add_prefixed_string (pedal)
        self.add_bytes (bytes([param]))
        self.add_float(val)
        return self.end_message ()


    def change_effect (self, pedal1, pedal2):
        cmd = 0x01
        sub_cmd = 0x06

        self.start_message (cmd, sub_cmd)
        self.add_prefixed_string (pedal1)
        self.add_prefixed_string (pedal2)
        return self.end_message ()

    def change_hardware_preset (self, preset_num):
        # preset_num is 0 to 3
        cmd = 0x01
        sub_cmd = 0x38

        self.start_message (cmd, sub_cmd)
        self.add_bytes (bytes([0]))
        self.add_bytes (bytes([preset_num]))         
        return self.end_message ()

    def turn_effect_onoff (self, pedal, onoff):
        cmd = 0x01
        sub_cmd = 0x15

        self.start_message (cmd, sub_cmd)
        self.add_prefixed_string (pedal)
        self.add_onoff (onoff)
        return self.end_message ()    


    def create_preset (self, preset):
        cmd = 0x01
        sub_cmd = 0x01
        this_chunk = 0

        self.start_message (cmd, sub_cmd, True)
        self.add_bytes (b'\x00\x7f')       
        self.add_long_string (preset["UUID"])
        self.add_string (preset["Name"])
        self.add_string (preset["Version"])
        descr = preset["Description"]
        if len (descr) > 31:
            self.add_long_string (descr)
        else:
            self.add_string (descr)
        self.add_string (preset["Icon"])
        self.add_float (120.0) #preset["BPM"])
        self.add_bytes (bytes([0x90 + 7]))        # always 7 pedals
        for i in range (0, 7):
            self.add_string (preset["Pedals"][i]["Name"])
            self.add_onoff (preset["Pedals"][i]["OnOff"])
            num_p = len(preset["Pedals"][i]["Parameters"])
            self.add_bytes (bytes([num_p + 0x90]))
            for p in range (0, num_p):
                self.add_bytes (bytes([p])) 
                self.add_bytes (b'\x91') ###
                self.add_float (preset["Pedals"][i]["Parameters"][p])
        self.add_bytes (bytes([preset["End Filler"]]))                   
        return self.end_message ()

