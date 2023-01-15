import bluetooth


if __name__=='__main__':
    bt_devices = bluetooth.discover_devices(lookup_names=True)

    address=None
    for addr, bt_name in bt_devices:
        if bt_name == 'Spark 40 Audio':
            address = addr

    if address:
        print("-----------------------------------------------")
        print("Add the following values to the config.py file")
        print("-----------------------------------------------")
        print("")
        print("amp_bt_address = '%s'"%address)
    else:
        print('Spark amp not found')
