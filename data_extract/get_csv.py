# -*- coding: utf-8 -*-
"""read mongodb database and save csv
"""
import os
import time
from datetime import datetime

from tqdm import tqdm
import numpy as np
from pymongo import MongoClient
from bartlett import Bartlett


mod_phase = lambda x: np.mod(x + np.pi, 2 * np.pi) - np.pi
database = "LocGPT"
ip = "158.132.255.174"
merge_collections = ["BlockP_leftbehind", "BlockP_leftbehind_setting2", "BlockP_right", "BlockP_rightfront", "BlockQ_behind", "BlockQ_behind_setting2", "BlockQ_left", "BlockR", "BlockR_setting2", "PQ504", "PQ504_corridor", "PQ504_meetingroom", "PQ505", "PQ512", "btw Q & T"]

## BLE channel
ble_ch_ind = [37]+[i for i in range(0, 11)] + [38] +[i for i in range(11,37)] + [39]
ble_ch_freq = np.linspace(2402e6, 2480e6, 40)
ble_freq_dict = dict(zip(ble_ch_ind, ble_ch_freq))
# print(ble_freq_dict)


def timestamp2uxtime(timestamp):
    # Convert the timestamp string to a datetime object
    try:
        timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    unix_time = time.mktime(timestamp_datetime.timetuple())
    unix_time = unix_time + timestamp_datetime.microsecond / 1e6

    return unix_time


def get_cfo_phase(gateway_constant_phase):
    """get cfo phase per sample (8 samples)
    """
    N = len(gateway_constant_phase)
    cfo_phase = mod_phase(gateway_constant_phase[1:] - gateway_constant_phase[:-1])
    cfo_phase = np.mean(cfo_phase)

    compensate_phase = cfo_phase * np.arange(N)
    phase_after_compensate = mod_phase(gateway_constant_phase - compensate_phase - gateway_constant_phase[0])
    # print(f"phase_after_compensate: {np.mean(phase_after_compensate)}")
    cfo = cfo_phase / (2 * np.pi * 1e-6)
    # print(f"cfo: {cfo}")

    return cfo_phase


def extract_integer_from_word(word):
    num = ""
    found_integer = False

    for char in word:
        if char.isdigit():
            num += char
            found_integer = True
        elif found_integer:
            break

    return int(num) if num else None


if __name__ == '__main__':

    ## create collection
    client = MongoClient(f"mongodb://tagsys:tagsys@{ip}:27017/")
    db = client[database]
    total_lens = 0
    for merge_collection in merge_collections:
        collection = db[merge_collection]
        data_len = collection.count_documents({})
        total_lens += data_len
        print(f"{merge_collection} has {data_len} records")
        data = collection.find({}, {'_id':0}).sort([("timestamp",1)]).allow_disk_use(True)

        # timestamp, freq, gateway_id, phase
        csv_data = np.zeros((data_len, 1+1+1+16))
        for i, item in tqdm(enumerate(data), desc="process", total=data_len):

            timestamp = timestamp2uxtime(item['timestamp'])
            tag_freq = ble_freq_dict[item['frequency']]
            csv_data[i,0] = timestamp
            csv_data[i,1] = tag_freq
            csv_data[i,2] = extract_integer_from_word(item["gateway"])

            gateway_tag_samples = np.array(item['samples']).reshape((-1,2))  # [82, 2] IQ samples
            gateway_tag_cfo_samples = gateway_tag_samples[:8] # [8, 2]
            gateway_tag_cfo_phase = np.angle(gateway_tag_cfo_samples[:,0]+1j*gateway_tag_cfo_samples[:,1])  # [8]
            gateway_tag_cfo_phase = get_cfo_phase(gateway_tag_cfo_phase)  # (1,)
            gateway_tag_compensate_phase = gateway_tag_cfo_phase * np.arange(0,32,2)
            gateway_tag_samplesV = gateway_tag_samples[9:9+32:2]  # [16, 2]
            gateway_tag_phase = np.angle(gateway_tag_samplesV[:,0]+1j*gateway_tag_samplesV[:,1])  # [16]
            gateway_tag_phase = gateway_tag_phase - gateway_tag_compensate_phase  # [16]
            gateway_tag_phase = mod_phase(gateway_tag_phase - gateway_tag_phase[0])  # ralative to the first phase
            csv_data[i, 3:19] = gateway_tag_phase

        csv_data[:,0] = csv_data[:,0] - csv_data[0,0]  # time offset
        csv_header = "timestamp, freq, gateway_id"
        phase_header = [f"p{j}" for j in range(1,17)]
        phase_header = ", ".join(phase_header)
        csv_header = csv_header + ", " + phase_header
        output_path = "./csv_data"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        np.savetxt(f"{output_path}/{merge_collection}.csv", csv_data, delimiter=",", header=csv_header, fmt='%.03f', comments="")
    print(total_lens)
