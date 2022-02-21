## UPDATE
# This script is designed to:
# 1. Collate user input
# 2. Preset the oscilloscope
# 3. Adjust the signal generator settings
# 4. Adjust oscilloscope settings
# 5. Send commands to MATLAB to connect to and instruct the oscilloscope

from cmath import log10
import math
import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import json

rm = pyvisa.ResourceManager()

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
        instrument.visa_timeout = 5000  # Timeout for VISA Read Operations
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


# -------------------------------
# OSCILLOSCOPE COMMANDS
# -------------------------------

def oscope_preset():
    "Resets the oscilloscope"
    command(oscope, '*DCL') # *DCL clears status registers
    command(oscope, '*CLS') # *CLS clears output queue
    command(oscope, '*RST') # *RST resets the scope


def oscope_default_settings(channel='1', acquisition_time = 0.01, horizontal_range='5.0', coupling='DC', offset='0.0', probe_scale='10'):
    command(oscope, f"TIM:ACQT{acquisition_time}")  # 10ms Acquisition time
    command(oscope, f"CHAN{channel}:RANG {horizontal_range}")  # Horizontal range 5V (0.5V/div)
    command(oscope, f"CHAN{channel}:OFFS {offset}")  # Offset 0
    command(oscope, f"CHAN{channel}:COUP {coupling}L")  # Coupling DC 1MOhm
    command(oscope, f"CHAN{channel}:STAT ON")  # Switch Channel ON
    command(oscope, f"CHAN{channel}:TYPE HRES")  # Set to High Resolution
    command(oscope, f'"PROB{channel}:SET:GAIN:MAN {probe_scale}')


def oscope_channel_switch(channel, on_off):
    "Switches channel on or off. Enter 1 to turn the channel on, 0 to turn the channel off"
    if on_off == '0':
        on_off == "OFF"
    elif on_off == '1':
        on_off = "ON"
    command(oscope, f"CHAN{channel}:STAT {on_off}")  # Switch Channel ON or OFF


def oscope_acq_time(acquisition_time):
    command(oscope, f"TIM:ACQT {acquisition_time}")  # 10ms Acquisition time


def oscope_range(channel, horizontal_range):
    command(oscope, f"CHAN{channel}:RANG {horizontal_range}")  # Horizontal range


def oscope_offset(channel, offset):
    command(oscope, f"CHAN{channel}:OFFS {offset}")  # Offset


def oscope_coupling(channel, coupling):
    command(oscope, f"CHAN{channel}:COUP {coupling}L")  # Coupling


def oscope_trigger_settings(channel, trigger_level=0):
    """Sets Trigger Settings"""
    command(oscope, "TRIG:A:MODE AUTO")  # Trigger Auto mode in case of no signal is applied
    command(oscope, "TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")  # Trigger to a positive rising edge
    command(oscope, f"TRIG:A:SOUR CH{channel}")  # Trigger source Channel set
    command(oscope, f"TRIG:A:LEV{trigger_level}")  # Trigger level set


def oscope_set_siggen(v, f, offset=0.0):
    command(oscope, ":WGENerator:OUTPut:LOAD HIGHz")
    command(oscope, ":WGEN:OUTPut ON")
    command(oscope, f":WGEN:VOLTage {v}")
    command(oscope, f":WGEN:VOLTage:OFFset {offset}")
    command(oscope, f":WGEN:FREQuency {f}")
    time.sleep(0.5) # to allow waveform to settle


def auto_adjust_timeaxis(chan, meas_chan=4):
    """Automatically adjusts the time axis."""

    # Time axis
    measurement_channel_setup(meas_chan, 'FREQ', chan)
    frequency = read_measurement(meas_chan)
    if frequency > 10e+10: # If the frequnecy cannot be measured, adjusts the timebase until a frequency will be obtainable
        command(oscope, f"TIMebase:RANGe 0.2")
        frequency = read_measurement(meas_chan)
    command(oscope, f"TIMebase:RANGe {2/(frequency)}")


def auto_adjust_voltageaxis(chan, meas_chan=4):
    """Automatically adjusts the voltage axis."""
    
    # Voltage axis
    measurement_channel_setup(meas_chan, 'PEAK', chan)
    voltage = read_measurement(meas_chan)
    vcheck = 80e-3
    while voltage > 10e+10: # If clipping zooms out until a reading can be taken
        command(oscope, f"CHANnel{chan}:RANGe {vcheck}")
        voltage = read_measurement(meas_chan)
        vcheck *= 10
    voltage *= 1.2
    command(oscope, f"CHANnel{chan}:RANGe {voltage}")
    vcheck2 = read_measurement(meas_chan)
    if vcheck2 > 10e+10:
        voltage *= 1.4
    command(oscope, f"CHANnel{chan}:RANGe {voltage}")


def auto_adjust(chan, meas_chan=4):
    """Autoscales so the waveform always fits the screen"""

    auto_adjust_timeaxis(chan, meas_chan)
    auto_adjust_voltageaxis(chan, meas_chan)


def measurement_channel_setup(meas_chan, meas_type, source_chan_1, source_chan_2=2):
    """Turns on measurement channels to record the desired values. Note: Phase is calculated as source_chan_2-source_chan_1"""
    
    command(oscope, f"MEASurement{meas_chan}:ON")
    if meas_type == 'PHASe':
        command(oscope, f"MEASurement{meas_chan}:SOURce CH{source_chan_2},CH{source_chan_1}") # Set sources to be chosen channels
        command(oscope, f"MEASurement{meas_chan}:MAIN {meas_type}")
    else:
        command(oscope, f"MEASurement{meas_chan}:SOURce CH{source_chan_1}")
        command(oscope, f"MEASurement{meas_chan}:MAIN {meas_type}")


def read_measurement(meas_chan, meas_type=0):
    """Reads a specified measurement channel."""

    time.sleep(1) # Needed to allow the waveform to settle
    if meas_type == 0:
        command(oscope, f"MEASurement{meas_chan}:RESult?")
    else:
        command(oscope, f"MEASurement{meas_chan}:RESult:{meas_type}?")
    time.sleep(0.6) # Time for the oscilloscope to load the result
    value_string = oscope.read()
    value = float(value_string)

    return value


def test_circuit(vin_PP, frequencies, chan1=1, chan2=2, meas_chan1=1, meas_chan2=2, meas_chan3=3):
    """Take measurements for the voltages and frequencies specified."""
    
    # Set up measurement channels
    measurement_channel_setup(meas_chan1, 'PEAK', chan1)
    measurement_channel_setup(meas_chan2, 'PEAK', chan2)
    measurement_channel_setup(meas_chan3, 'PHASe', chan1, chan2)

    # Set trigger level
    oscope_trigger_settings(chan1)

    #Initiate result variables
    v_in_list = []
    v_out_list = []
    phase_list = []
    results_dict = {} 

    # Run tests
    oscope_set_siggen(vin_PP[0],frequencies[0]) # Turn on the signal generator
    auto_adjust_timeaxis(chan1)
    for v in vin_PP:
        command(oscope, f":WGEN:VOLTage {v}") # Set the voltage
        auto_adjust_voltageaxis(chan1)
        for f in frequencies:
            command(oscope, f":WGEN:FREQuency {f}") # Set the frequency
            auto_adjust_timeaxis(chan1)
            auto_adjust_voltageaxis(chan2)
            # Take measurements and record data
            v_in = read_measurement(meas_chan1)
            v_out = read_measurement(meas_chan2)
            phase = read_measurement(meas_chan3)
            v_in_list.append(v_in)
            v_out_list.append(v_out)
            phase_list.append(phase)
            results_dict[f"v={v} f={f}"] = (v_in, v_out, phase)

    return results_dict


def freq_response(results, frequencies):
    """Returns the frequency response from the data provided by the test_circuit function."""
    
    freq_resp=[]
    freq_resp_dB=[]
    for f in frequencies:
        gainlist=[]
        for v in Vin_PP:
            gainlist.append(results[f'v={v} f={f}'][1]/results[f'v={v} f={f}'][0])
        gain_avg = sum(gainlist)/len(gainlist)
        freq_resp.append(gain_avg)
        freq_resp_dB.append(10*(math.log10(gain_avg)))
    
    return freq_resp, freq_resp_dB


def acquire_waveform(chan, vinpp, frequency, offset=0.0):
    """Acquire waveform."""

    vin=vinpp/2 # vinpp is the pk-pk amplitude
    timespan=1/(frequency*2)  # initialise time span to two periods of the signal of frequency

    # SET UP CHANNEL
    command(oscope, 'CHAN1:TYPE HRES')
    command(oscope, 'FORM UINT,16;FORM?')
    form = oscope.read()
    command(oscope, f'TIM:SCAL {timespan}')
    command(oscope, f'CHAN1:RANG {vinpp*2.5}')

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

    time.sleep(0.5)

    # DATA ACQUISITION LOOP
    command(oscope, f'CHAN{chan}:DATA?')
    bin_size = oscope.baud_rate # determine data bin size
    iterations = int(num_samples)/bin_size # calculate number of bins/iterations
    iter_no=ceil(iterations)-1; # round iterations to the next integer and minus 1 so that only data in the buffer is read
    iter_no *= 2 # times by 2 as uint16 data is requested
    headerdata = oscope.read_bytes(8) # removes header
    waveform_data = np.array([])
    
    for k in range(iter_no-1):
        temp_data = oscope.read_bytes(int(bin_size)) #'int16') # read the data in the current bin. We are
        mv = memoryview(temp_data).cast('H')
        bin_data = np.array(mv)
        if k == 0:
            print("BIN:", bin_data)
        waveform_data = np.append(waveform_data, bin_data)
        #  reading bin_size/2 elements of type ‘int16’(word).
        #  each ‘int16’ is two bytes long, so bin_size bytes are read.
        #temp_data = int.from_bytes(temp_data, 'big')
        # add the elements to the data vector, 'waveform_data'
    
    # CONVERTS WAVEFORM DATA TO VALUES
    no_of_data_array_elements = len(waveform_data)
    times = [i * float(x_inc) + float(x_or) for i in range(no_of_data_array_elements)]
    voltages = waveform_data * float(y_inc) + float(y_or) 

    # PLOT WAVEFORM
    plt.plot(times,voltages)
    plt.show()

    # RUN THE OSCILLOSCOPE
    command(oscope, 'RUN')

    return times, voltages


def characterise_filter(start_freq=100, end_freq=100000, points_per_decade=10):
    """Characterises a filter."""

    vin_PP = [1]
    frequencies=[100,200,300,400,500,600,700,800,900,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000]
    results = test_circuit(vin_PP, frequencies)
    freq_resp, freq_resp_dB = freq_response(results, frequencies)
    plot_freq_response(frequencies, freq_resp_dB)
    print("SUCCESS")
    print("HERE", (freq_resp_dB[0]-freq_resp_dB[int(len(frequencies)*0.3)]))
    if (freq_resp_dB[0]-freq_resp_dB[int(len(frequencies)*0.3)]) > (freq_resp_dB[int(len(frequencies)*0.7)]-freq_resp_dB[-1]):
        print("Low-Pass")
    else:
        print("High-pass")

# -------------------------------
# PLOTTING FUNCTIONS
# -------------------------------

def plot_freq_response(frequencies, freq_resp_dB):
    """Plots the frequency response of the circuit."""

    plt.plot(frequencies, freq_resp_dB)
    plt.semilogx()
    plt.ylabel('Gain (dB)')
    plt.xlabel('Frequency (Hz)')
    plt.title('Frequency Response')
    plt.show(block=False)
    plt.show()

# -------------------------------
# RECORD MEASUREMENTS FROM THE OSCILLOSCOPE
# -------------------------------

# Main

# Connect to Instruments
quick = 1
oscope = connect_instrument(oscilloscope1_string)
instruments = [oscope]
if quick == 0:
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

# Set up oscilloscope
oscope_preset()
oscope_default_settings(1)
oscope_default_settings(2)

# Set parameters
Vin_PP = [1]
Offset = 0.0
Frequencies = [100,250,500,750,1000,2500,5000,7500,10000,25000,50000,75000,100000]

# Recieve user input
#Input = open('testjson.json', 'r')
#Data = json.loads(Input.read())
#Vin_PP = [Data['voltage_AC_amplitude']]
#Offset = [Data['voltage_DC']]
#Frequencies = [int(Data['voltage_AC_frequency_from']), int(Data['voltage_AC_frequency_to'])]
#Input.close()
#print(Vin_PP, Offset, Frequencies)

# Test circuit at specified voltages and frequencies
#Results = test_circuit(Vin_PP, Frequencies)
#print(Results)

characterise_filter()

# Return the frequency response of the circuit
#Freq_resp, Freq_resp_dB = freq_response(Results, Frequencies)

# Plot
#plot_freq_response(Frequencies, Freq_resp_dB)
