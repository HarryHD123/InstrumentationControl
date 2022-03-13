import math
import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
from DataManagement import *
from GraphTools import plot_freq_resp
import json
import GUI_tk
from importlib import reload

rm = pyvisa.ResourceManager()
oscope = None

# -------------------------------
# CONNECTING TO DEVICES
# -------------------------------
# Change these string to suit your devices
oscilloscope1_string = 'TCPIP0::192.168.1.2::inst0::INSTR'
multimeter1_string = 'TCPIP0::192.168.1.5::5025::SOCKET'
signalgenerator1_string = 'TCPIP0::192.168.1.3::inst0::INSTR'
powersupply1_string = 'TCPIP0::192.168.1.4::inst0::INSTR'


# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def command(instrument, command):
    "Writes to oscilloscope"
    print(instrument.write(command))


def read(instrument, command):
    "Reads from oscilloscope"
    info = instrument.query(command)

    return info


# ------------------
# SETUP FUNCTIONS SETTINGS
# -----------------

def connect_instrument(instrument_string):
    instrument = None
    try:
        # adjust the VISA Resource string to fit your instrument
        instrument = rm.open_resource(instrument_string)
        instrument.read_termination = '\n'  # Define the last line of an input to be a paragraph break
        instrument.write_termination = '\n'  # Set the output (to the instrument) to be end with a paragraph break
        instrument.baud_rate = 512  # Set buffer size to be 512
        instrument.visa_timeout = 10000  # Timeout for VISA Read Operations
        instrument.opc_timeout = 3000  # Timeout for opc-synchronised operations
        instrument.instrument_status_checking = True  # Error check after each command
    except Exception as ex:
        print('Error initializing the instrument ' + instrument_string + ' session:\n' + ex.args[
            0])  # Gives error message if connection fails
        pass

    return instrument


def req_info(instrument):
    "Requests information from the oscilloscope"
    idn = read(instrument, '*IDN?')
    print(f"\nHello, I am: '{idn}'")


def connect_all_instruments(oscilloscope1_string = 'TCPIP0::192.168.1.2::inst0::INSTR', multimeter1_string = 'TCPIP0::192.168.1.5::5025::SOCKET', signalgenerator1_string = 'TCPIP0::192.168.1.3::inst0::INSTR', powersupply1_string = 'TCPIP0::192.168.1.4::inst0::INSTR'):
    
    oscope = connect_instrument(oscilloscope1_string)
    mmeter = connect_instrument(multimeter1_string)
    psource = connect_instrument(powersupply1_string)
    siggen = connect_instrument(signalgenerator1_string)
    instruments = [oscope, mmeter, psource, siggen]

    for instrument in instruments:
        try:
            req_info(instrument)
            print(f"Successfully connected to {instrument}")
        except Exception:
            print(f"Connection to {str(instrument)} failed")

    return oscope, mmeter, psource, siggen
# -------------------------------
# OSCILLOSCOPE COMMANDS
# -------------------------------

def oscope_preset(oscope):
    "Resets the oscilloscope"
    command(oscope, '*DCL') # *DCL clears status registers
    command(oscope, '*CLS') # *CLS clears output queue
    command(oscope, '*RST') # *RST resets the scope


def oscope_default_settings(oscope, channel='1', acquisition_time = 0.01, horizontal_range='5.0', coupling='DC', offset='0.0', probe_scale='10'):
    command(oscope, f"TIM:ACQT{acquisition_time}")  # 10ms Acquisition time
    command(oscope, f"CHAN{channel}:RANG {horizontal_range}")  # Horizontal range 5V (0.5V/div)
    command(oscope, f"CHAN{channel}:OFFS {offset}")  # Offset 0
    command(oscope, f"CHAN{channel}:COUP {coupling}L")  # Coupling DC 1MOhm
    command(oscope, f"CHAN{channel}:STAT ON")  # Switch Channel ON
    command(oscope, f"CHAN{channel}:TYPE HRES")  # Set to High Resolution
    command(oscope, f'"PROB{channel}:SET:GAIN:MAN {probe_scale}')


def oscope_channel_switch(oscope, channel, on_off):
    "Switches channel on or off. Enter 1 to turn the channel on, 0 to turn the channel off"
    if on_off == '0':
        on_off == "OFF"
    elif on_off == '1':
        on_off = "ON"
    command(oscope, f"CHAN{channel}:STAT {on_off}")  # Switch Channel ON or OFF


def oscope_acq_time(oscope, acquisition_time):
    command(oscope, f"TIM:ACQT {acquisition_time}")  # 10ms Acquisition time


def oscope_range(oscope, channel, horizontal_range):
    command(oscope, f"CHAN{channel}:RANG {horizontal_range}")  # Horizontal range


def oscope_offset(oscope, channel, offset):
    """Sets the DC ofset level."""

    command(oscope, f"CHAN{channel}:OFFS {offset}")  # Offset


def oscope_coupling(oscope, channel, coupling):
    """Sets the coupling mode."""

    command(oscope, f"CHAN{channel}:COUP {coupling}L")  # Coupling


def oscope_trigger_settings(oscope, channel, trigger_level=0):
    """Sets Trigger Settings."""

    command(oscope, "TRIG:A:MODE AUTO")  # Trigger Auto mode in case of no signal is applied
    command(oscope, "TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")  # Trigger to a positive rising edge
    command(oscope, f"TRIG:A:SOUR CH{channel}")  # Trigger source Channel set
    command(oscope, f"TRIG:A:LEV{trigger_level}")  # Trigger level set


def oscope_set_siggen(oscope, v, f, offset=0.0):

    command(oscope, ":WGENerator:OUTPut:LOAD HIGHz")
    command(oscope, ":WGEN:OUTPut ON")
    command(oscope, f":WGEN:VOLTage {v}")
    command(oscope, f":WGEN:VOLTage:OFFset {offset}")
    command(oscope, f":WGEN:FREQuency {f}")
    time.sleep(0.5) # to allow waveform to settle


def auto_adjust_timeaxis(oscope, chan, meas_chan=4):
    """Automatically adjusts the time axis."""

    # Time axis
    measurement_channel_setup(oscope, meas_chan, 'FREQ', chan)
    frequency = read_measurement(oscope, meas_chan)
    while frequency > 10e+10: # If the frequnecy cannot be measured, adjusts the timebase until a frequency will be obtainable
        command(oscope, f"TIMebase:RANGe 0.2")
        frequency = read_measurement(oscope, meas_chan)
    command(oscope, f"TIMebase:RANGe {2/(frequency)}")


def auto_adjust_voltageaxis(oscope, chan, meas_chan=4):
    """Automatically adjusts the voltage axis."""
    
    # Voltage axis
    measurement_channel_setup(oscope, meas_chan, 'PEAK', chan)
    voltage = read_measurement(oscope, meas_chan)
    vcheck = 80e-3
    while voltage > 10e+10: # If clipping zooms out until a reading can be taken
        command(oscope, f"CHANnel{chan}:RANGe {vcheck}")
        voltage = read_measurement(oscope, meas_chan)
        vcheck *= 10
    voltage *= 1.2
    command(oscope, f"CHANnel{chan}:RANGe {voltage}")
    vcheck2 = read_measurement(oscope, meas_chan) # Check for clipping due to offset
    if vcheck2 > 10e+10:
        voltage *= 1.4
    command(oscope, f"CHANnel{chan}:RANGe {voltage}")


def auto_adjust(oscope, chan, meas_chan=4):
    """Autoscales so the waveform always fits the screen"""

    auto_adjust_timeaxis(oscope, chan, meas_chan)
    auto_adjust_voltageaxis(oscope, chan, meas_chan)


def measurement_channel_setup(oscope, meas_chan, meas_type, source_chan_1, source_chan_2=2):
    """Turns on measurement channels to record the desired values. Note: Phase is calculated as source_chan_2-source_chan_1"""
    
    command(oscope, f"MEASurement{meas_chan}:ON")

    if meas_type == 'PHASe':
        command(oscope, f"MEASurement{meas_chan}:SOURce CH{source_chan_2},CH{source_chan_1}") # Set sources to be chosen channels
        command(oscope, f"MEASurement{meas_chan}:MAIN {meas_type}")
    else:
        command(oscope, f"MEASurement{meas_chan}:SOURce CH{source_chan_1}")
        command(oscope, f"MEASurement{meas_chan}:MAIN {meas_type}")


def read_measurement(oscope, meas_chan, meas_type=0, statistics=False):
    """Reads a specified measurement channel."""

    if statistics:
        command(oscope, f"MEASurement{meas_chan}:STATistics:RESet")
        time.sleep(2) # Needed to statistics to be reset and some values taken
        #command(oscope, f"MEASurement{meas_chan}:STATistics:VALue?")
        command(oscope, f"MEASurement{meas_chan}:RESult:AVG?")
    else:
        time.sleep(0.5) # Needed to allow the waveform to settle
        if meas_type == 0:
            command(oscope, f"MEASurement{meas_chan}:RESult?")
        else:
            command(oscope, f"MEASurement{meas_chan}:RESult:{meas_type}?")        

    time.sleep(0.75) # Time for the oscilloscope to load the result
    value_string = oscope.read()
    value = float(value_string)

    return value


def acquire_waveform(oscope, chan, plot_graph=False):
    """Acquire waveform."""

    # SET UP CHANNEL
    auto_adjust(oscope, chan)

    command(oscope, 'CHAN1:TYPE HRES')
    command(oscope, 'FORM UINT,16;FORM?')
    time.sleep(0.1)
    form = oscope.read()

    # READ HEADER AND CALCULATION VARIABLES
    command(oscope, f'CHAN{chan}:DATA:HEAD?')
    header = str(oscope.read()).split(',')
    X_start = header[0]
    X_stop = header[1]
    num_samples = header[2]
    val_per_samp = header[3]
    command(oscope, 'SING;*OPC?')
    time.sleep(0.5)
    opc = oscope.read()
    command(oscope, f'CHAN{chan}:DATA:POIN DMAX')
    command(oscope, f'CHAN{chan}:DATA:POIN?')
    d_points = oscope.read()
    command(oscope, f'CHAN{chan}:DATA:YRES?')
    y_res = float(oscope.read())
    command(oscope, f'CHAN{chan}:DATA:XOR?')
    x_or = float(oscope.read())
    command(oscope, f'CHAN{chan}:DATA:XINC?')
    x_inc = float(oscope.read())
    command(oscope, f'CHAN{chan}:DATA:YOR?')
    y_or = float(oscope.read())
    command(oscope, 'FORM UINT,16;FORM?')
    form = oscope.read()
    command(oscope, 'FORM:BORD LSBF')
    command(oscope, f'CHAN{chan}:DATA:YINC?')
    y_inc = float(oscope.read())
    time.sleep(0.1)

    # DATA ACQUISITION LOOP
    command(oscope, f'CHAN{chan}:DATA?')
    bin_size = oscope.baud_rate # determine data bin size
    iterations = int(num_samples)/bin_size # calculate number of bins/iterations
    iter_no = math.ceil(iterations)-1; # round iterations to the next integer and minus 1 so that only data in the buffer is read
    iter_no *= 2 # times by 2 as uint16 data is requested
    headerdata = oscope.read_bytes(8) # removes header
    waveform_data = np.array([])
    
    for k in range(iter_no-1):
        temp_data = oscope.read_bytes(int(bin_size)) #'int16') # read the data in the current bin. We are
        mv = memoryview(temp_data).cast('H')
        bin_data = np.array(mv)
        waveform_data = np.append(waveform_data, bin_data)
        # reading bin_size/2 elements of type ‘int16’(word).
        # each ‘int16’ is two bytes long, so bin_size bytes are read.
        # add the elements to the data vector, 'waveform_data'
    
    # CONVERTS WAVEFORM DATA TO VALUES
    no_of_data_array_elements = len(waveform_data)
    times = [i * float(x_inc) + float(x_or) for i in range(no_of_data_array_elements)]
    voltages = waveform_data * float(y_inc) + float(y_or) 

    # PLOT WAVEFORM
    if plot_graph:
        plt.figure(2)
        plt.plot(times,voltages)
        plt.ylabel('Voltage (V))')
        plt.xlabel('Time (s)')
        plt.title('Waveform')
        #plt.autoscale()
        plt.grid(which='both')
        plt.show(block=False)
        plt.show()

    # RUN THE OSCILLOSCOPE
    command(oscope, 'RUN')

    return times, voltages


def test_circuit(oscope, vin_PP, frequencies, siggen=None, chan1=1, chan2=2, meas_chan1=1, meas_chan2=2, meas_chan3=3, statistics=True):
    """Take measurements for the voltages and frequencies specified.
    A frequency response is found for the results of this testing.
    This frequency response can be plotted by setting plot_freq_resp=True.
    A cutoff(dB) value can be found by setting cutoff=True. The cutoff value is set to -3dB by default, but can be changed by setting cutoff_dB_val equal to your specified value."""
    
    # Set up measurement channels
    measurement_channel_setup(oscope, meas_chan1, 'PEAK', chan1)
    measurement_channel_setup(oscope, meas_chan2, 'PEAK', chan2)
    measurement_channel_setup(oscope, meas_chan3, 'PHASe', chan1, chan2)
    if statistics:
        command(oscope, "MEASurement:STATistics ON")

    # Set trigger level
    oscope_trigger_settings(oscope, chan1)

    if siggen != None:
        siggen_set_siggen(siggen, vin_PP[0],frequencies[0])
    else:
        oscope_set_siggen(oscope, vin_PP[0],frequencies[0]) # Turn on the signal generator

    time.sleep(3) # Time for oscilloscope to set intial settings

    #Initiate result variables
    v_in_list = []
    v_out_list = []
    phase_list = []
    results_dict = {} 
 
    # Run tests
    for v in vin_PP:
        if siggen == None:
            command(oscope, f":WGEN:VOLTage {v}") # Set the voltage
        command(oscope, f"CHANnel1:RANGe {v*1.2}") # Adjust input channel to correctly read the input voltage
        for f in frequencies:
            print(v, f)
            if siggen == None:
                command(oscope, f":WGEN:FREQuency {f}") # Set the frequency
            elif siggen != None:
                siggen_set_siggen(siggen, v, f)
            command(oscope, f"TIMebase:RANGe {2/(f)}")
            auto_adjust_voltageaxis(oscope, chan2) # Readjust the output channel to correctly read output voltage
            # Take measurements and record data
            v_in = read_measurement(oscope, meas_chan1, statistics=statistics)
            v_out = read_measurement(oscope, meas_chan2, statistics=statistics)
            phase = read_measurement(oscope, meas_chan3, statistics=statistics)
            v_in_list.append(v_in)
            v_out_list.append(v_out)
            phase_list.append(phase)
            results_dict[f"v={v} f={f}"] = (v_in, v_out, phase)

    # ALL AUTO ADJUST
    # # Run tests
    # auto_adjust(chan1) # Adjust the scope
    # for v in vin_PP:
    #     command(oscope, f":WGEN:VOLTage {v}") # Set the voltage
    #     auto_adjust_voltageaxis(chan1) # Adjust input channel to correctly read the input voltage
    #     for f in frequencies:
    #         command(oscope, f":WGEN:FREQuency {f}") # Set the frequency
    #         auto_adjust_timeaxis(chan1) # Readjust the time axis
    #         auto_adjust_voltageaxis(chan2) # Readjust the output channel to correctly read output voltage
    #         # Take measurements and record data
    #         v_in = read_measurement(meas_chan1, statistics=statistics)
    #         v_out = read_measurement(meas_chan2, statistics=statistics)
    #         phase = read_measurement(meas_chan3, statistics=statistics)
    #         v_in_list.append(v_in)
    #         v_out_list.append(v_out)
    #         phase_list.append(phase)
    #         results_dict[f"v={v} f={f}"] = (v_in, v_out, phase)

    return results_dict


def characterise_filter(oscope, siggen=None, vin_PP=[1], freq_min=100, freq_max=100000, points_per_dec=10, cutoff_dB_val=-3, freq_resp_graph=True, statistics=True):
    """Characterises a filter and reutrns whether the filter is high or low pass.
    By setting quick_sim=True, 4 points per decade are used instead of the standard 10 to speed up the process.
    A graph can be plotted by setting plot_graph=True when calling the function. 
    Interpolation is used to smooth the graph as standard when quick_sim is called.
    The cutoff_3dB is added to the graph as a standard, calculated using Pchip Interpolation"""

    # Calculate the frequencies to test along
    frequencies = points_list_maker(freq_min,freq_max,points_per_dec)


    # Test circuit and find the frequency response
    results = test_circuit(oscope, vin_PP, frequencies, siggen=siggen, statistics=statistics)
    freq_resp, freq_resp_dB, cutoff_freq = calc_freq_response(results, vin_PP, frequencies, cutoff_dB_val=cutoff_dB_val)

    # Calculates whether the filter is high or low pass
    if (abs(freq_resp_dB[0]-freq_resp_dB[int(len(frequencies)*0.3)])) < abs((freq_resp_dB[int(len(frequencies)*0.7)]-freq_resp_dB[-1])):
        filter_type = "Low-Pass"
        print("Low-Pass")
    else:
        filter_type = "High-Pass"
        print("High-pass")

    if freq_resp_graph:
        plot_freq_resp(frequencies, freq_resp_dB, cutoff_dB_val, cutoff_freq)

    return filter_type


# -------------------------------
# SIGNAL GENERATOR FUNCTIONS
# -------------------------------

def siggen_set_siggen(siggen, v, f, offset=0.0):
    command(siggen, ":WGENerator:OUTPut:LOAD HIGHz")
    command(siggen, ":WGEN:OUTPut ON")
    command(siggen, f":WGEN:VOLTage {v}")
    command(siggen, f":WGEN:VOLTage:OFFset {offset}")
    command(siggen, f":WGEN:FREQuency {f}")
    time.sleep(0.5) # to allow waveform to settle

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    oscope = connect_instrument(oscilloscope1_string)
    mmeter = connect_instrument(multimeter1_string)
    psource = connect_instrument(powersupply1_string)
    siggen = connect_instrument(signalgenerator1_string)
    instruments = [oscope, mmeter, psource, siggen]

    for instrument in instruments:
        try:
            req_info(instrument)
            print(f"Successfully connected to {instrument}")
        except Exception:
            print(f"Connection to {str(instrument)} failed")
    

# Connect to Instruments
# quick = 1
# oscope = connect_instrument(oscilloscope1_string)
# instruments = [oscope]
# if quick == 0:
#     mmeter = connect_instrument(multimeter1_string)
#     psource = connect_instrument(powersupply1_string)
#     siggen = connect_instrument(signalgenerator1_string)
#     instruments = [oscope, mmeter, psource, siggen]

# for instrument in instruments:
#     try:
#         req_info(instrument)
#         print(f"Successfully connected to {instrument}")
#     except Exception:
#         print(f"Connection to {str(instrument)} failed")

# # Set up oscilloscope
# oscope_preset()
# oscope_default_settings(1)
# oscope_default_settings(2)

# Set parameters
Vin_PP = [0.4,1,5]
Offset = 0.0
Frequencies = [100,1000,10000,100000,1000000]
Vin_PP = [5]

Cutoff_dB_val = -3

# Recieve user input
#Input = open('testjson.json', 'r')
#Data = json.loads(Input.read())
#Vin_PP = [Data['voltage_AC_amplitude']]
#Offset = [Data['voltage_DC']]
#Frequencies = [int(Data['voltage_AC_frequency_from']), int(Data['voltage_AC_frequency_to'])]
#Input.close()
#print(Vin_PP, Offset, Frequencies)

# Test circuit at specified voltages and frequencies and calculate the frequency response
#Results = test_circuit(Vin_PP, Frequencies)
#Freq_resp, Freq_resp_dB, Cutoff_freq = calc_freq_response(Results, Vin_PP, Frequencies, cutoff_dB_val=Cutoff_dB_val)

# Plot the frequency response
#plot_freq_resp(Frequencies, Freq_resp_dB, Cutoff_dB_val, Cutoff_freq)

#print("Results", Results)
#print("Freqresp_dB", Freq_resp_dB)
#print("Cutoff", Cutoff_freq)

# Characterise filter
#Filter_Type = characterise_filter(statistics=False)

# Acquire waveform
#oscope_set_siggen(3,20000)
#Times, Voltages = acquire_waveform(2)
