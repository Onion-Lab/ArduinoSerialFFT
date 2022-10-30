from datetime import datetime
import pandas as pd
import numpy as np
import serial
from scipy import signal
from scipy.integrate import simps
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

# Byte codes
CONNECT = 0xc0
SYNC = 0xaa
EXCODE = 0x55
POOR_SIGNAL = 0x02
ATTENTION = 0x04
MEDITATION = 0x05
BLINK = 0x16
RAW_VALUE = 0x80
ASIC_EEG_POWER = 0x83

SAMPLE_RATE = 512


class BrainWaveDataParser(object):
    def __init__(self, parser_name=None):
        ############### List Size ###############
        self.LIST_SIZE = 10
        ########################################

        self.input_data = ""
        self.parse_data = self.parse_data()
        self.state = ""
        self.sending_data = False
        self.raw_data = []
        self.noise_data = []
        self.attention_data = []
        self.meditation_data = []
        self.data_limit = 1024
        self.eSense_data_limit = 5 
        self.raw_data_bytes = 512

        self.dataList = []

        self.Result = []

        next(self.parse_data)

    def get_data(self, data, data_limit):
        self.data_limit = data_limit
        for c in data:
            self.parse_data.send(c)

    def costomFFT(self) :
        HighAlpha = []
        LowBeta = []
        for data in self.dataList :
           HighAlpha.append(data['high-alpha']) # 갑자기 증가, 갑자기 감소
           LowBeta.append(data['low-beta'])

        temp = []

        HighAlphaSpectrum = np.fft.fft(HighAlpha)
        LowBetaSpectrum = np.fft.fft(LowBeta)

        ####################### spectrum #######################
        temp.append(HighAlphaSpectrum)
        temp.append(LowBetaSpectrum)
        #######################################################

        ####################### magnitude #######################
        temp.append(np.abs(HighAlphaSpectrum))
        temp.append(np.abs(LowBetaSpectrum))
        #######################################################

        ####################### phase ########################
        temp.append(np.angle(HighAlphaSpectrum))
        temp.append(np.angle(LowBetaSpectrum))
        #######################################################

        self.Result.append(np.array(temp))
        print("FFT Complete")

        #################### Insert Yout Code ####################

        # data['high-alpha'] -> 센서에서 10번 high-alpha 값을 받아옴
        # if data['high-alpha'] > 어떤 조건일 때 :
        #     print("현재 졸고 있습니다.")
        # elif data['high-alpha'] > 어떤 조건일 때 :
        #     print("현재 집중하고 있습니다.")
        print("##########################")
        print(HighAlpha)
        print()
        print(LowBeta)
        print("##########################")
        ##########################################################

    def parse_data(self):
        while 1:
            byte = yield
            if byte == SYNC:
                byte = yield
                if byte == SYNC:
                    packet_length = yield
                    packet_code = yield
                    if packet_code == CONNECT:
                        self.state = "connected"

                    else:
                        self.sending_data = True
                        left = packet_length - 2
                        while left > 0:
                            if packet_code == ASIC_EEG_POWER:  # Bands
                                vector_length = yield
                                current_vector = []
                                for row in range(8):
                                    band_low_byte = yield
                                    band_middle_byte = yield
                                    band_high_byte = yield
                                    value = (band_high_byte << 16) | (band_middle_byte << 8) | band_low_byte
                                    current_vector.append(value)

                                left -= vector_length

                                bands_array = np.array(current_vector)
                                bands_normalized = bands_array / bands_array.sum()
                                # assign bands
                                band_data = {
                                             "high-alpha": bands_normalized[3],
                                             "low-beta": bands_normalized[4],
                                             }
                                self.dataList.append(band_data)
                                
                                if len(self.dataList) == self.LIST_SIZE:
                                    self.costomFFT()
                                    self.dataList = []

                            packet_code = yield
                else:
                    pass  # sync failed
            else:
                pass  # sync failed

def mindwave_connect(serial_port, baud_rate=57600, bytesize=8, parity='N', stopbits=1, timeout=None, number_of_byte=512):
    ser = serial.Serial(serial_port)
    ser.port = serial_port
    ser.baudrate = baud_rate
    ser.bytesize = bytesize
    ser.parity = parity
    ser.stopbits = stopbits
    ser.timeout = timeout
    
    return ser

######################### 포트지정 ##########################
port_address = 'COM7'
#############################################################

number_of_bytes = 512

mindwave_data = mindwave_connect(port_address, timeout=None, number_of_byte=number_of_bytes)
print("Mindwave connected to {}".format(port_address))
brain_data = BrainWaveDataParser()

try:
    while True:
        brain_data.get_data(mindwave_data.read(512), number_of_bytes)
except KeyboardInterrupt:
    import os
    import pandas as pd
    
    forderName = str(datetime.now()).replace(":","-")+"/"

    if not os.path.exists(forderName):
        os.makedirs(forderName)

    for data in np.array(brain_data.Result):
        print(data)
        filename = str(datetime.now()).replace(":","-")+".csv"
        dataframe = pd.DataFrame(data.T, columns=['HighAlphaSpectrum','LowBetaSpectrum','HighAlphaMagnitude','LowBetaMagnitude','HighAlphaPhase','LowBetaPhase'])
        dataframe.to_csv(forderName+filename,sep=',',na_rep='NaN')
        print(dataframe)



