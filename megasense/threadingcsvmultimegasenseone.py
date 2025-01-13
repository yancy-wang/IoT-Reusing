#!/bin/env python3.6

import logging
import threading
import time
import binascii
import struct

from datetime import datetime
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException, UUID

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device - {}".format(dev.addr))
        elif isNewData:
            print("Received new data from - {}".format(dev.addr))


def mega_scan(verbose):
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10.0)

    for dev in devices:
        if verbose:
            print("Device MAC {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData(): 
                print (" {} = {} ({})".format(desc, value, adtype)) 
        else:
            print("Device MAC {}".format(dev.addr), end='')
            for (adtype, desc, value) in dev.getScanData():
                if desc == "Short Local Name": 
                    print (" {}".format(value))

def mega_connect(mega_mac, addr_type):
    try:
        print("Connecting to megasense one ({}, {})".format(mega_mac, addr_type))
        mega_connection = Peripheral(mega_mac, addr_type)
        return mega_connection
    except BTLEException as e:
        print("Error in connecting to Megasense one")
        print("Real error {}".format(e))
        return 0

def mega_list_services(connection):
    if connection == 0:
        return connection
    try:
        print("Asking for service")
        mega_services = connection.getServices()
        for item in mega_services:
            print(item)
    except BTLEException as e:
        print("Error in listing services from Megasense one")
        print("Real error {}".format(e))

def mega_get_service(connection, uuid, verbose=False):
    if connection == 0:
        return connection
    try:
        if verbose:
            print("Getting service handle... {}".format(uuid))
        megaservice = connection.getServiceByUUID(UUID(uuid))
        return megaservice
    except BTLEException as e:
        print("Error in getting service from Megasense one")
        print("Real error {}".format(e))
        return 0

def mega_get_characteristics(service, verbose=False):
    if service == 0:
        return service
    try:
        if verbose:
            print("Getting characteristics...")
        mega_chars = service.getCharacteristics()
        return mega_chars
    except BTLEException as e:
        print("Error in getting chars from Megasense one")
        print("Real error {}".format(e))
        return 0

def mega_write_int_config_characteristic(conn, value, write_to_uuid, wait_for_response = False, verbose = False):
    try:
        if verbose:
            print("Getting characteristics for writing...")
        ch = conn.getCharacteristics(uuid=write_to_uuid)[0]
        print(ch)
        print(ch.getHandle())
        conn.writeCharacteristic(ch.getHandle(), value.to_bytes(2, byteorder='little'), wait_for_response)
    except BTLEException as e:
        print("Error in writing to characteristic on Megasense one")
        print("Real error {}".format(e))
        return 0
    return 1

def mega_read_characteristic(connection, char_uuid, verbose=False):
    if connection == 0:
        return connection
    try:
        ch = connection.getCharacteristics(uuid=char_uuid)[0]
        if verbose:
            print(ch)
        if (ch.supportsRead()):
            val = ch.read()
            val = binascii.b2a_hex(val)
            val = val.decode()
            if verbose:
                print ("Value {}".format(val))
            return val
    except BTLEException as e:
        print("Error in reading char value from Megasense one")
        print("Real error {}".format(e))
        return 0

def unpack_bme(byte_value):
    retdict = {}
    bme_temperature = byte_value[0:8]
    temperature = int.from_bytes(bytes.fromhex(bme_temperature), byteorder='little')/100
    retdict["temperature_c"] = temperature
    bme_humidity = byte_value[8:16]
    humidity = int.from_bytes(bytes.fromhex(bme_humidity), byteorder='little')/1000
    retdict["humidity_prcnt"] = humidity
    bme_pressure = byte_value[16:24]
    pressure = int.from_bytes(bytes.fromhex(bme_pressure), byteorder='little')/10000
    retdict["pressure_hpa"] = pressure
    return retdict

def unpack_speco3(byte_value):
    retdict = {}
    spe_ozone = byte_value[0:8]
    ozone = int.from_bytes(bytes.fromhex(spe_ozone), byteorder='little')
    retdict["ozone_ppm"] = ozone
    spe_ozone_volt = byte_value[8:16]
    ozone_volt = int.from_bytes(bytes.fromhex(spe_ozone_volt), byteorder='little', signed=True)
    retdict["ozone_mvolt"] = ozone_volt
    return retdict

def unpack_mic(byte_value):
    retdict = {}
    mic_eq = byte_value[0:8]
    eq = struct.unpack('<f', bytes.fromhex(mic_eq))
    retdict["eq_db"] = eq
    mic_1smin = byte_value[8:16]
    onesmin = struct.unpack('<f', bytes.fromhex(mic_1smin))
    retdict["1s_min_db"] = onesmin
    mic_1smax = byte_value[16:24]
    onesmax = struct.unpack('<f', bytes.fromhex(mic_1smax))
    retdict["1s_max_db"] = onesmax
    return retdict

def unpack_mics(byte_value):
    retdict = {}
    mics_co = byte_value[0:4]
    co = int.from_bytes(bytes.fromhex(mics_co), byteorder='little')  
    retdict["co_ppm"] = co
    mics_no2 = byte_value[4:8]
    no2 = int.from_bytes(bytes.fromhex(mics_no2), byteorder='little')  
    retdict["no2_ppb"] = no2
    mics_covolt = byte_value[8:16]
    covolt = int.from_bytes(bytes.fromhex(mics_covolt), byteorder='little', signed=True)  
    retdict["co_mvolt"] = covolt
    mics_no2volt = byte_value[16:24]
    no2volt = int.from_bytes(bytes.fromhex(mics_no2volt), byteorder='little', signed=True)  
    retdict["no2_mvolt"] = no2volt
    return retdict

def unpack_tvoc(byte_value):
    retdict = {}
    sgp_tvoc = byte_value[0:8]
    tvoc = int.from_bytes(bytes.fromhex(sgp_tvoc), byteorder='little')  
    retdict["tvoc_ppb"] = tvoc
    return retdict

def unpack_batt(byte_value):
    retdict = {}
    batt_percentage = byte_value[0:2]
    percent = int.from_bytes(bytes.fromhex(batt_percentage), byteorder='little')
    retdict["batt_prcnt"] = percent
    batt_voltage = byte_value[2:10]
    voltage = int.from_bytes(bytes.fromhex(batt_voltage), byteorder='little')
    retdict["batt_mvolt"] = voltage
    return retdict

def unpack_sps(byte_value):
    retdict = {}
    sps_nc0p5 = byte_value[0:8]
    nc0p5 = struct.unpack('<f', bytes.fromhex(sps_nc0p5))
    retdict["nc_0p5_npcm3"] = nc0p5
    sps_nc1p0 = byte_value[8:16]
    nc1p0 = struct.unpack('<f', bytes.fromhex(sps_nc1p0))
    retdict["nc_1p0_npcm3"] = nc1p0
    sps_nc2p5 = byte_value[16:24]
    nc2p5 = struct.unpack('<f', bytes.fromhex(sps_nc2p5))
    retdict["nc_2p5_npcm3"] = nc2p5
    sps_nc4p0 = byte_value[24:32]
    nc4p0 = struct.unpack('<f', bytes.fromhex(sps_nc4p0))
    retdict["nc_4p0_npcm3"] = nc4p0
    sps_nc10p0 = byte_value[32:40]
    nc10p0 = struct.unpack('<f', bytes.fromhex(sps_nc10p0))
    retdict["nc_10p0_npcm3"] = nc10p0        
    sps_mc1p0 = byte_value[40:48]
    mc1p0 = struct.unpack('<f', bytes.fromhex(sps_mc1p0))
    retdict["Mc_1p0_ugpm3"] = mc1p0
    sps_mc2p5 = byte_value[48:56]
    mc2p5 = struct.unpack('<f', bytes.fromhex(sps_mc2p5))
    retdict["Mc_2p5_ugpm3"] = mc2p5
    sps_mc4p0 = byte_value[56:64]
    mc4p0 = struct.unpack('<f', bytes.fromhex(sps_mc4p0))
    retdict["Mc_4p0_ugpm3"] = mc4p0
    sps_mc10p0 = byte_value[64:72]
    mc10p0 = struct.unpack('<f', bytes.fromhex(sps_mc10p0))
    retdict["Mc_10p0_ugpm3"] = mc10p0
    sps_typpm = byte_value[72:80]
    typpm = struct.unpack('<f', bytes.fromhex(sps_typpm))
    retdict["Typical_particle_size_um"] = typpm
    return retdict

def unpack_lis(byte_value):
    retdict = {}
    lis_x = byte_value[0:8]
    x = struct.unpack('<f', bytes.fromhex(lis_x))
    retdict["x_g"] = x
    lis_y = byte_value[8:16]
    y = struct.unpack('<f', bytes.fromhex(lis_y))
    retdict["y_g"] = y
    lis_z = byte_value[16:24]
    z = struct.unpack('<f', bytes.fromhex(lis_z))
    retdict["z_g"] = z               
    lis_rx = byte_value[24:28]
    rx = int.from_bytes(bytes.fromhex(lis_rx), byteorder='little')  
    retdict["Raw_x"] = rx
    lis_ry = byte_value[28:32]
    ry = int.from_bytes(bytes.fromhex(lis_ry), byteorder='little')  
    retdict["Raw_y"] = ry
    lis_rz = byte_value[32:36]
    rz = int.from_bytes(bytes.fromhex(lis_rz), byteorder='little')  
    retdict["Raw_z"] = rz
    return retdict

def unpack_si(byte_value):
    retdict = {}
    si_lux = byte_value[0:8]
    lux = struct.unpack('<f', bytes.fromhex(si_lux))
    retdict["Lux_lx"] = lux
    si_uv = byte_value[8:16]
    uv = struct.unpack('<f', bytes.fromhex(si_uv))
    retdict["Uv_mwpm2"] = uv
    return retdict

def unpack_interval(name, byte_value):
    retdict = {}
    interval_value = byte_value[0:4]
    interval = int.from_bytes(bytes.fromhex(interval_value), byteorder='little')
    retdict[name] = interval
    return retdict

def unpack_big(value):
    all_dict = {}
    tmp_dict = {}
    byte_value = bytes(len(value))
    byte_value = value
    #order in byte_value
    #bme280 (24), mic (24), mics4514 (24), lis3dh (36), si1133 (16), sps30 (80), ozone (16), tvoc (8), batt (10)
    # length with the intervals 286 was 238
    # length now 290 as the version code added
    #byte is always 2 as string format could have used bytes but easier to debug
    tmp_dict = unpack_bme(byte_value[0:24])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_mic(byte_value[24:48])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_mics(byte_value[48:72])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_lis(byte_value[72:108])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_si(byte_value[108:124])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_sps(byte_value[124:204])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_speco3(byte_value[204:220])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_tvoc(byte_value[220:228])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_batt(byte_value[228:238])
    all_dict = {**all_dict, **tmp_dict}
    #intervals
    tmp_dict = unpack_interval("bme280_int",byte_value[238:242])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("speco3_int",byte_value[242:246])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("mic_int",byte_value[246:250])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("mics4514_int",byte_value[250:254])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("mics4514pre_int",byte_value[254:258])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("sgoc3_int",byte_value[258:262])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("sps30_int",byte_value[262:266])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("sps30pre_int",byte_value[266:270])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("lis3dh_int",byte_value[270:274])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("si1133_int",byte_value[274:278])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("batt_int",byte_value[278:282])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("leds_on",byte_value[282:286])
    all_dict = {**all_dict, **tmp_dict}
    tmp_dict = unpack_interval("code_version",byte_value[286:290])
    all_dict = {**all_dict, **tmp_dict}

    return all_dict

def mega_decode_values(item, ret_val, verbose=False):
    retdict = {}
    byte_value = bytes(len(ret_val))
    byte_value = ret_val
    if item == "BME280":
        retdict = unpack_bme(byte_value)
    elif item == "SPEC03":
        retdict = unpack_speco3(byte_value)
    elif item == "MIC":
        retdict = unpack_mic(byte_value)
    elif item == "MICS4514":
        retdict = unpack_mics(byte_value)
    elif item == "TVOC":
        retdict = unpack_tvoc(byte_value)
    elif item == "BATTERY":
        retdict = unpack_batt(byte_value)
    elif item == "SPS30":
        retdict = unpack_sps(byte_value)
    elif item == "LIS3DH":
        retdict = unpack_lis(byte_value)                
    elif item == "SI1133":
        retdict = unpack_si(byte_value)
    elif item == "ALL_IN_ONE":
        retdict = unpack_big(byte_value)    
    elif item == "BME280INT":
        bme_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(bme_int), byteorder='little')  
        retdict["Si_interval_s"] = inter        
    elif item == "SPECO3INT":
        spec_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(spec_int), byteorder='little')  
        retdict["Spec_interval_s"] = inter        
    elif item == "BATTERYINT":
        batt_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(batt_int), byteorder='little')  
        retdict["Batt_interval_s"] = inter
    elif item == "MICINT":
        mic_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(mic_int), byteorder='little')  
        retdict["Mic_interval_s"] = inter        
    elif item == "MICS4514INT":
        mics_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(mics_int), byteorder='little')  
        retdict["Mics_interval_s"] = inter
    elif item == "MICS4514PREHEATINT":
        micspre_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(micspre_int), byteorder='little')  
        retdict["Mics_pre_interval_s"] = inter
    elif item == "SGPC3INT":
        sgp_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(sgp_int), byteorder='little')  
        retdict["Sgp_interval_s"] = inter        
    elif item == "SPS30INT":
        sps_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(sps_int), byteorder='little')  
        retdict["Sps_interval_s"] = inter
    elif item == "SPS30PREFANINT":
        spspre_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(spspre_int), byteorder='little')  
        retdict["Sps_pre_interval_s"] = inter    
    elif item == "LIS3DHINT":
        li_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(li_int), byteorder='little')  
        retdict["Li_interval_s"] = inter
    elif item == "SI1133INT":
        si_int = byte_value[0:8]
        inter = int.from_bytes(bytes.fromhex(si_int), byteorder='little')  
        retdict["Si_interval_s"] = inter
    elif item == "LEDSONOFF":
        m_leds = byte_value[0:8]
        leds = int.from_bytes(bytes.fromhex(m_leds), byteorder='little')  
        retdict["Leds_onoff_0off"] = leds
    elif item == "CODE_VERSION":
        m_cversion = byte_value[0:8]
        cversion = int.from_bytes(bytes.fromhex(m_cversion), byteorder='little')  
        retdict["Code_version"] = cversion
    else:
        print("Unknown item")
    if verbose:
        print(retdict)
    return retdict

def get_char_value(connections, chars_dict, verbose=False):
    for conn in connections:
        all_dicts = {}
        if verbose:
            print("Started reading characteristic values...")
        before = datetime.now()    
        for item in chars_dict:   
            if verbose:
                print(".", end='')
            ret_val = mega_read_characteristic(conn, chars_dict[item], False)
            if verbose:
                print("Read {} characters".format(len(ret_val)))
            ret_dict = mega_decode_values(item, ret_val, False)
            all_dicts = {**all_dicts, **ret_dict}
        after = datetime.now()    
        d = after-before
        line = f"{after.strftime('%Y-%m-%dT%H:%M:%S')},{conn.addr},"
        for x in all_dicts:
                line = line + f"{all_dicts[x]},"
                if verbose:
                    print(f"{x} :: {all_dicts[x]}")
        line = line[:-1]
        print(line)

def connect_one(chars_dict, dev, mac, silent):
    target_addr_type = "random"
    conn = 0
    if not silent:
        print("Device name: {} mac: {}".format(dev, mac))
    for char in chars_dict:
        if not silent:
            print("Char name : {} uuid: {}".format(char, chars_dict[char]))
        #conn = mega_connect(mac, target_addr_type)
        if conn == 0: 
            print("ERROR connection {}= {}".format(dev, mac))
            continue
        if not silent:
            print("Connected {}= {}".format(dev, mac))
        return conn

def connect_list_of_devices(device_list, chars_dict, silent):
    conns = []
    for device in device_list:
        conns.append(connect_one(device, device_list[device], chars_dict, silent))
    return conns

def thread_function(name, mac, chars_dict, sleep_interval, silent):
    logging.info(f"Thread {name}({mac}): starting ,interval for sleep: {sleep_interval}")
    conn = []
    conn.append(connect_one(chars_dict, name, mac, silent))
    while 1:
        print(name)
        time.sleep(10)
        get_char_value(conn, chars_dict, verbose=False)
        time.sleep(sleep_interval)
    logging.info(f"Thread {name}({mac}): finishing")

def main_multi_threading(device_list, chars_dict, header, silent):
    print(header)
    threads = []
    for dev in device_list:
        new_thread = threading.Thread(target=thread_function, args=(dev,device_list[dev],chars_dict,0,silent,))
        new_thread.name = dev
        #die when main dies
        new_thread.daemon = True
        threads.append(new_thread)
    for thrds in threads:
        thrds.start()

def main_multi(device_list, chars_dict,header,silent=False):
    connections = connect_list_of_devices(device_list, chars_dict, silent)
    print(header)
    while 1:
        get_char_value(connections, chars_dict, verbose=False)

def main_single(target_device, chars_dict, target_service, test_write=False, list_services_and_characteristics=False):
    target_addr_type = "random"

    conn = mega_connect(target_device, target_addr_type)
    if conn == 0: 
        print("Connection problem, exiting")
        return
    if test_write:
        #Test out the writing by turning of the leds and waiting and turning them on again
        write_service_leds ="3f4d1701-188d-46bd-869b-e87f342aa36e"
        print("Waiting a bit (5 secs) to see that it connected")
        time.sleep(5)
        print("Trying to write, if it succeeds led turns off")
        ret = mega_write_int_config_characteristic(conn, 0, write_service_leds, False, True)
        if ret == 0:
            print("Failed to write, exiting")
            conn.disconnect()
            return 
        print("led should be off waiting a bit (5 secs) and turning it on again")
        time.sleep(5)
        ret = mega_write_int_config_characteristic(conn, 1, write_service_leds, False, True)
        if ret == 0:
            print("Failed to write, exiting")
            conn.disconnect()
            return 
        print("Led should be on again")

    if  list_services_and_characteristics:
        mega_list_services(conn, False)
        serv = mega_get_service(conn, target_service, False)
        if serv == 0:
            return
        chars = mega_get_characteristics(serv)
        if chars == 0:
            return 
        for item in chars:
            print(item)

    while 1:
        all_dicts = {}
        print("Started reading characteristic values...")
        before = datetime.now()    
        for item in chars_dict:   
            print(".", end='')
            ret_val = mega_read_characteristic(conn, chars_dict[item], True)
            print("Read {} characters".format(len(ret_val)))
            ret_dict = mega_decode_values(item, ret_val, False)
            all_dicts = {**all_dicts, **ret_dict}
        after = datetime.now()    
        d = after-before
        print("time-now: {}".format(after))
        print("\rReading took = {} s".format(d.total_seconds()))
        print(all_dicts)
        time.sleep(1)    

if __name__ == "__main__":
    #format = "%(asctime)s,%(message)s"
    format = "%(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%Y-%m-%dT%H:%M:%S")
    
    target_device_arnab = "d6:2a:a1:7a:af:f3" 
    target_device_hope77 = "d8:96:be:30:b7:a3" 
    target_device_test = "f5:c2:de:b9:5d:cc" 

    #max five for my laptop
    device_list_ilmari_school = {
        "HEL01": "C5:C1:72:C1:3E:32",
        "HEL02": "C9:AB:6D:3F:8A:69",
        "HEL03": "D2:D6:21:53:B9:1C",
        "HEL04": "E1:77:83:8E:EB:33",
        "HEL05": "D4:7F:9D:A4:14:20"
    }

    device_list_windtest = {
        "BIKE": "F5:C2:DE:B9:5D:CC",
        "RUNNER": "EA:5D:F2:9E:74:53"
    }

    device_list_just_testing = {
        "N1": "ED:03:86:C4:65:D1", 
        "N2": "FE:3E:8A:03:F9:9D", 
        "I1": "D0:31:F7:A1:15:76", 
        "I2": "EB:F0:9E:16:C4:61", 
        "I3": "E3:CB:F6:CA:1D:C5"  
    }

    device_list_optimal_placement = {
        "HOPE45": "D7:B6:C3:C4:C7:C5",
        "HOPE89": "C8:71:91:04:E5:A2"
        #"HOPE37": "E4:77:BF:66:5D:F4",
        #"HOPE69": "FB:42:ED:26:AE:D2",
        #"HOPE53": "C7:B3:6A:4F:FB:DF",
        #"HOPE14": "EB:C9:E2:F3:50:E9",
        #"HOPE11": "EF:29:10:F9:97:39",
        #"HOPE85": "F9:5D:31:AE:F4:71",
        #"HOPE91": "E1:D7:89:EF:4F:F8",
        #"HOPE58": "E0:AE:DB:5A:AC:37",
        #"HOPE61": "C3:68:7A:9B:47:3A",
        #"HOPE67": "CD:81:67:BB:39:87",
        #"HOPE56": "C5:25:67:FC:A4:03",
        #"HOPE80": "D1:91;C4:48:02:4F",
        #"HOPE83": "FE:6B:22:14:E6:64",
        #"HOPE82": "DA:51:59:20:38:6E",
        #"HOPE74": "D5:D3:E9:56:17:D8",
        #"HOPE63": "C7:CE:2E:E3:7C:72",
        #"HOPE79": "C6:11:3B:90:40:AC",
        #"HOPE02": "FD:4C:34:5A:84:F3",
    }

    mega_chars = {
        "BME280": "3f4d1801-188d-46bd-869b-e87f342aa36e",
        "SPEC03": "3f4d1802-188d-46bd-869b-e87f342aa36e",
        "MIC": "3f4d1803-188d-46bd-869b-e87f342aa36e",
        "MICS4514": "3f4d1804-188d-46bd-869b-e87f342aa36e",
        "TVOC": "3f4d1805-188d-46bd-869b-e87f342aa36e",
        "SPS30": "3f4d1806-188d-46bd-869b-e87f342aa36e",
        "LIS3DH": "3f4d1807-188d-46bd-869b-e87f342aa36e",
        "SI1133": "3f4d1808-188d-46bd-869b-e87f342aa36e",
        "ALL_IN_ONE": "3f4d1809-188d-46bd-869b-e87f342aa36e",
        "BME280INT": "3f4d1501-188d-46bd-869b-e87f342aa36e",
        "SPECO3INT": "3f4d1502-188d-46bd-869b-e87f342aa36e",
        "MICINT": "3f4d1503-188d-46bd-869b-e87f342aa36e",
        "MICS4514INT": "3f4d1504-188d-46bd-869b-e87f342aa36e",
        "SGPC3INT": "3f4d1505-188d-46bd-869b-e87f342aa36e",
        "SPS30INT": "3f4d1506-188d-46bd-869b-e87f342aa36e",
        "BATTERYINT": "3f4d1601-188d-46bd-869b-e87f342aa36e",
        "SPS30PREFANINT": "3f4d1602-188d-46bd-869b-e87f342aa36e",
        "MICS4514PREHEATINT": "3f4d1603-188d-46bd-869b-e87f342aa36e",
        "SI1133INT": "3f4d1507-188d-46bd-869b-e87f342aa36e",
        "LIS3DHINT": "3f4d1508-188d-46bd-869b-e87f342aa36e",
        "LEDSONOFF": "3f4d1701-188d-46bd-869b-e87f342aa36e",
        "BATTERY": "3f4d1901-188d-46bd-869b-e87f342aa36e"
    }

    mega_service = "3f4d1809-188d-46bd-869b-e87f342aa36e"

    mega_chars_all_in_one = {
        "ALL_IN_ONE": "3f4d1809-188d-46bd-869b-e87f342aa36e"
    }

    csvheader = "time, mac,temperature_c,humidity_prcnt,pressure_hpa,eq_db,1s_min_db,1s_max_db," \
              + "co_ppm,no2_ppb,co_mvolt,no2_mvolt,x_g,y_g,z_g,Raw_x,Raw_y,Raw_z,Lux_lx,Uv_mwpm2," \
              + "nc_0p5_npcm3,nc_1p0_npcm3,nc_2p5_npcm3,nc_4p0_npcm3,nc_10p0_npcm3,Mc_1p0_ugpm3," \
              + "Mc_2p5_ugpm3,Mc_4p0_ugpm3,Mc_10p0_ugpm3,Typical_particle_size_um,ozone_ppm," \
              + "ozone_mvolt,tvoc_ppb,batt_prcnt,batt_mvolt,bme280_int,speco3_int,mic_int,mics4514_int," \
              + "mics4514pre_int,sgoc3_int,sps30_int,sps30pre_int,lis3dh_int,si1133_int,batt_int," \
              + "leds_on,code_version"

    #Uncomment to do a scan in the start. Need to be sudo.
    #mega_scan(True)

    #main_single(target_device_test, mega_chars_all_in_one, target_service, test_write=False, list_services_and_characteristics=False)
    #main_multi(device_list_windtest, mega_chars_all_in_one, csvheader, Silent=False)
    #main_multi(device_list_ilmari_school, mega_chars_all_in_one, csvheader, Silent=False)
    main_multi_threading(device_list_optimal_placement, mega_chars_all_in_one, csvheader, silent=False)
