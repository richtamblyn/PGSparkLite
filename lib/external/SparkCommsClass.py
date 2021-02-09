class SparkComms:
    def __init__(self, bt_sock):
        self.bt_sock = bt_sock

    def send_it(self, dat):
        self.bt_sock.send(dat)

    def read_it(self, dat_len):
        dat = self.bt_sock.recv(dat_len)
        return dat

    # helper functions to request preset and send acknowledgements
    def send_ack(self, seq, cmd):
        ack = bytes.fromhex("01fe000041ff17000000000000000000f001" +
                            "%0.2X" % seq + "0004" + "%0.2X" % cmd + "f7")
        self.send_it(ack)

    def send_preset_request(self, preset):
        preset_hex = "%0.2x" % preset
        arg = ("01fe000053fe3c000000000000000000" +
               "f0010400" + "0201" +
               "00" + "00" + preset_hex +
               "00000000000000000000000000000000" +
               "00000000000000000000000000000000" + "0000f7")
        self.send_it(bytes.fromhex(arg))

    # core function to read a block from serial or bluetooth

    def get_block(self):
        rd_data = b''
        read_len = 1
        a = -1
        while a == -1:
            rd_data += self.read_it(read_len)
            a = rd_data.find(b'\x01\xfe')
            if a >= 0:
                # found the start, trim of anything before that
                rd_data = rd_data[a:]
                while len(rd_data) < 7:
                    rd_data += self.read_it(read_len)
                blk_len = rd_data[6]
                while len(rd_data) < blk_len:
                    rd_data += self.read_it(read_len)

                res = rd_data[:blk_len]
                rd_data = rd_data[blk_len:]
        return res

    # get_data will read a number of blocks from get_block,
    # dependent on whether this is a multi-chunk message or not

    def get_data(self):
        resp = []
        last_block = False

        while not last_block:
            blk = self.get_block()
            resp.append(blk)

            blk_len = blk[6]
            direction = blk[4:6]
            seq = blk[18]
            cmd = blk[20]
            sub_cmd = blk[21]

            if direction == b'\x53\xfe' and cmd == 0x01 and sub_cmd != 0x04:
                # the app sent a message that needs a response
                self.send_ack(seq, cmd)

            # now we need to see if this is the last block

            # if the block length is less than the max size then
            # definitely last block
            # could be a full block and still last one
            # but to be full surely means it is a multi-block as
            # other messages are always small
            # so need to check the chunk counts - in different places
            # depending on whether

            if direction == b'\x53\xfe':
                if blk_len < 0xad:
                    last_block = True
                else:
                    # this is sent to Spark so will have a chunk header at top
                    num_chunks = blk[23]
                    this_chunk = blk[24]
                    if this_chunk + 1 == num_chunks:
                        last_block = True

            if direction == b'\x41\xff':
                if blk_len < 0x6a:
                    last_block = True
                else:
                    # this is from Spark so chunk header could be anywhere
                    # so search from the end
                    pos = blk.rfind(b'\xf0\x01')
                    try:
                        num_chunks = blk[pos+7]
                        this_chunk = blk[pos+8]
                        if this_chunk + 1 == num_chunks:
                            last_block = True
                    except:
                        pass
        return resp
