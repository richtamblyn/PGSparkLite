########
#
# Spark Class
#
# Class to read commands sent to Positive Grid Spark
#
# See https://github.com/paulhamsh/Spark-Parser

# Use:  reader = SparkReadMessage()
#       reader.set_message(preset)
#       reader.read_message()
#
#       reader.text is a text representation
#       reader.raw is a raw unformatted text representation
#       reader.pyhon is a python dict representation
#
#       reader.data is the input bytes
#       reader.message is the 8 bit data in the message

import struct


class SparkReadMessage:
    def __init__(self):
        self.data = b''
        self.message = []
        self.current_preset = None

    def set_message(self, msg):
        self.data = msg
        self.message = []
        
    def structure_data(self):
        self.cmd=0
        self.sub_cmd=0
        block_content = b''

        # remove all the block headers and concatenate the contents
        # no point in retaining the block structure as chunks can span blocks
        # in messages received from Spark

        for block in self.data:
            block_length = block[6]
            if len (block) != block_length:
                print ("Block is length %d and reports %d" % (len(block), block_length))
            
            chunk = block[16:]
            block_content += chunk

        # and split them into chunks now, splitting on each f7

        chunk_temp = b''
        chunks=[]
        for by in block_content:
            chunk_temp += bytes([by])
            if by == 0xf7:
                chunks.append(chunk_temp)
                chunk_temp = b''
                
            
        # remove the chunk headers, saving the command and sub_command
        # and convert the 7 bit data to 8 bits
        
        chunk_8bit=[]
        for chunk in chunks:
            this_cmd = chunk[4]
            this_sub_cmd = chunk[5]
            data7bit = chunk[6:-1]

            chunk_len = len (data7bit)
            num_seq = int ((chunk_len + 7) / 8)
            data8bit = b''
            
            for this_seq in range (0, num_seq):
                seq_len = min (8, chunk_len - (this_seq * 8))
                seq = b''
                bit8 = data7bit[this_seq * 8]
                for ind in range (0,seq_len-1):
                    dat = data7bit[this_seq * 8 + ind + 1]
                    if bit8 & (1<<ind) == (1<<ind):
                        dat |= 0x80
                    seq +=  bytes([dat])
                data8bit += seq
                
            chunk_8bit.append([this_cmd, this_sub_cmd, data8bit])   
            
        # now check for mult-chunk messages and collapse their data into a single message
        # multi-chunk messages are cmd/sub_cmd of 1,1 or 3,1
        
        self.message=[]
        concat_data=b''
        for chunk in chunk_8bit:
            this_cmd     = chunk[0]
            this_sub_cmd = chunk[1]
            this_data = chunk[2]
            if this_cmd in [1,3] and this_sub_cmd == 1:
                #found a multi-message
                num_chunks = this_data[0]
                this_chunk = this_data[1]
                concat_data += this_data[3:]
                # if at last chunk of multi-chunk
                if this_chunk == num_chunks -1:
                    self.message.append([this_cmd, this_sub_cmd, concat_data])
                    concat_data=b''
            else:
                # copy old one
                self.message.append([this_cmd, this_sub_cmd, this_data])

    #########################################   
        
    def read_byte(self):
        a_byte = self.msg[self.msg_pos]
        self.msg_pos += 1
        return a_byte


    def read_prefixed_string(self):
        str_len = self.read_byte()
        str_len2 = self.read_byte() - 0xa0
        a_str = ""
        for i in range (0, str_len2):
            a_str += chr(self.read_byte())
        return a_str
    
    def read_string(self):
        a_byte = self.read_byte()
        
        if a_byte == 0xd9:
            a_byte = self.read_byte()
            str_len = a_byte
        elif a_byte >= 0xa0:
            str_len = a_byte - 0xa0
        else:
            a_byte = self.read_byte()
            str_len = a_byte - 0xa0

        a_str = ""
        for i in range (0, str_len):
            a_str += chr(self.read_byte())
        return a_str       

    # floats are special - bit 7 is actually stored in the format byte and not in the data
    def read_float (self):
        prefix = self.read_byte() # should be ca
        flt_bytes = b''
        for i in range (0,4):
            flt_bytes += bytes([self.read_byte()])
        [val] = struct.unpack(">f", flt_bytes)
        return val

           
    def read_onoff (self):
        a_byte = self.read_byte()
        if a_byte == 0xc3:
            return "On"
        elif a_byte == 0xc2:
            return "Off"
        else:
            return "?"
    
    #############################

    def start_str(self):
        self.text = ""
        self.python = "{"
        self.raw = ""
        self.dict={}
        self.indent = ""

    def end_str (self):
        self.python += "}"

    def add_indent(self):
        self.indent += "\t"

    def del_indent(self):
        self.indent = self.indent[:-1]

    def add_python(self, python_str):
        self.python += self.indent + python_str + "\n"
        
    def add_str(self, a_title, a_str, nature = "alL"):
        self.raw += a_str+ " "
        self.text += self.indent+ "%-20s" %  a_title+":"+ a_str + "\n"
        if nature != "python":
            self.python += self.indent + "\""+a_title+"\":\""+ a_str + "\",\n"

    def add_int(self, a_title, an_int, nature = "all"):
        self.raw += "%d" % an_int + " "
        self.text += self.indent + "%-20s" % a_title+ ":" + "%d" % an_int + "\n"
        if nature != "python":
            self.python += self.indent+ "\"" +a_title+ "\":" + "%d" % an_int + ",\n"

    def add_float(self, a_title, a_float, nature = "all"):
        self.raw += "%2.4f" % a_float + " "
        self.text += self.indent + "%-20s" % a_title+ ":" + "%2.4f" % a_float + "\n"
        if nature == "python":
            self.python += self.indent + "%2.4f" % a_float  +",\n"
        else:
            self.python += self.indent + "\"" +a_title+ "\": " + "%2.4f" % a_float  +",\n"           
        
    ######## Functions to package a command for the Spark


    def read_effect_parameter (self):
        self.start_str()
        effect = self.read_prefixed_string ()
        param = self.read_byte ()
        val = self.read_float()
        self.add_str ("Effect", effect)
        self.add_int ("Parameter", param)
        self.add_float ("Value", val)
        self.end_str()

    def read_effect (self):
        self.start_str()
        effect1 = self.read_prefixed_string ()
        effect2 = self.read_prefixed_string ()
        self.add_str ("OldEffect", effect1)
        self.add_str ("NewEffect", effect2)
        self.end_str()

    def read_bpm(self):
        self.start_str()
        self.read_byte()
        self.read_byte()        
        bpm = self.read_byte()                          
        self.add_float("BPM", bpm)
        self.end_str()

    def read_current_preset_number(self):        
        # Cache this preset value, apply it to the next inbound Preset message
        self.read_byte()
        self.current_preset = self.read_byte()        

    def read_hardware_preset (self):
        self.start_str()
        self.read_byte ()
        preset_num = self.read_byte ()
        self.add_int ("NewPreset", preset_num)
        self.end_str()
        
    def read_store_hardware_preset (self):
        self.start_str()
        self.read_byte ()
        preset_num = self.read_byte ()
        self.add_int ("NewStoredPreset", preset_num)
        self.end_str()
        
    def read_effect_onoff (self):
        self.start_str()
        effect = self.read_prefixed_string ()
        onoff = self.read_onoff ()
        self.add_str ("ChangeEffectState", effect)
        self.add_str ("OnOff", onoff)
        self.end_str()

    def read_preset (self):
        self.start_str()
        self.read_byte ()

        preset = self.read_byte()

        if self.current_preset != None:
            preset = self.current_preset
            self.current_preset = None

        self.add_int ("PresetNumber", preset)

        uuid = self.read_string ()
        self.add_str ("UUID", uuid)
        name = self.read_string ()
        self.add_str ("Name", name)
        version = self.read_string ()
        self.add_str ("Version", version)
        descr = self.read_string ()
        self.add_str ("Description", descr)

        icon = self.read_string ()
        self.add_str("Icon", icon)
        bpm = self.read_float ()
        self.add_float ("BPM", bpm)
        
        self.add_python("\"Pedals\": [")
        self.add_indent()

        for i in range (0, 7):
            e_str = self.read_string ()
            e_onoff = self.read_onoff ()
            self.add_python ("{")
            self.add_str ("Name", e_str)
            self.add_str ("OnOff", e_onoff)
            num_p = self.read_byte() - 0x90
            self.add_python("\"Parameters\":[")
            self.add_indent()
            for p in range (0, num_p):
                num = self.read_byte() 
                spec = self.read_byte ()
                val = self.read_float()
                self.add_int ("Parameter", num, "python")
                self.add_str ("Special", hex(spec), "python")
                self.add_float ("Value", val, "python")
            self.add_python("],")
            self.del_indent()
            self.add_python("},")
        self.add_python("],")
        self.del_indent()
        unk = self.read_byte()
        self.add_str("Unknown", hex(unk))
        self.end_str()


    ########################
                
    def set_interpreter (self, msg):
        self.msg = msg
        self.msg_pos = 0

    def run_interpreter (self, cmd, sub_cmd):
        if cmd == 0x01:
            if sub_cmd == 0x01:
                self.read_preset()
            elif sub_cmd == 0x04:
                self.read_effect_parameter()
            elif sub_cmd == 0x06:
                self.read_effect()
            elif sub_cmd == 0x15:
                self.read_effect_onoff()
            elif sub_cmd == 0x38:
                self.read_hardware_preset()
            else:
                print(hex(cmd), hex(sub_cmd), "not handled")
        elif cmd == 0x03:
            if sub_cmd == 0x01:
                self.read_preset()
            elif sub_cmd == 0x06:
                self.read_effect()
            elif sub_cmd == 0x10:                
                self.read_current_preset_number()                
            elif sub_cmd == 0x15:
                self.read_effect_onoff()
            elif sub_cmd == 0x27:
                self.read_store_hardware_preset()
            elif sub_cmd == 0x37:
                self.read_effect_parameter()
            elif sub_cmd == 0x38:
                self.read_hardware_preset()
            elif sub_cmd == 0x63:
                self.read_bpm()
            else:
                print(hex(cmd), hex(sub_cmd), "not handled")       
        elif cmd == 0x04:
            print ("Acknowledgement")
        else:
            print ("Unprocessed")
        return 1
        
    def interpret_data(self):
        for msg in self.message:
            this_cmd = msg[0]
            this_sub_cmd = msg[1]
            this_data = msg[2]

            self.set_interpreter(this_data)
            self.run_interpreter(this_cmd, this_sub_cmd)
            

    def read_message(self):
        self.structure_data()
        self.interpret_data()
        return self.message
