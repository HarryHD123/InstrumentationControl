## UPDATE
# This script is designed to:
# 1. Collate user input
# 2. Preset the oscilloscope
# 3. Adjust the signal generator settings
# 4. Adjust oscilloscope settings
# 5. Send commands to MATLAB to connect to and instruct the oscilloscope

from math import ceil
import pyvisa
import time
import array
import numpy as np
import matplotlib.pyplot as plt

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


def oscope_default_settings(channel='1', acquisition_time = 0.01, horizontal_range='5.0', coupling='DC', offset='0.0'):
    command(oscope, f"TIM:ACQT {acquisition_time}")  # 10ms Acquisition time
    command(oscope, f"CHAN{channel}:RANG {horizontal_range}")  # Horizontal range 5V (0.5V/div)
    command(oscope, f"CHAN{channel}:OFFS {offset}")  # Offset 0
    command(oscope, f"CHAN{channel}:COUP {coupling}L")  # Coupling DC 1MOhm
    command(oscope, f"CHAN{channel}:STAT ON")  # Switch Channel ON
    command(oscope, f"CHAN{channel}:TYPE HRES")  # Set to High Resolution


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


def oscope_trigger_settings(channel, trigger_level):
    """Sets Trigger Settings"""
    command(oscope, "TRIG:A:MODE AUTO")  # Trigger Auto mode in case of no signal is applied
    command(oscope, "TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")  # Trigger type Edge Positive
    #command(oscope,'TRIGger:SLOpe POSitive')
    command(oscope, f"TRIG:A:SOUR CH{channel}")  # Trigger source Channel set
    command(oscope, f"TRIG:A:LEV{trigger_level}")  # Trigger level set

#command(oscope,':TRIGger:EDGE:SOURce channel3');
#command(oscope,'TRIGger:MODE EDGE');                 
#command(oscope,'TRIGger:SLOpe POSitive');
#command(oscope,'TRIGger:LEVel 0');

def oscope_set_siggen(v, f, offset=0.0):
    command(oscope, ":WGENerator:OUTPut:LOAD HIGHz")
    command(oscope, ":WGEN:OUTPut ON")
    command(oscope, f":WGEN:VOLTage {v}")
    command(oscope, f":WGEN:VOLTage:OFFset {offset}")
    command(oscope, f":WGEN:FREQuency {f}")


def auto_adjust(v, f, chan, meas_chan): # FIX
    """Autoscales so the waveform always fits the screen"""

    # Initial time axis adjustment
    f # a test frequency, testf, is used to work out the initial settings. testf is set to the first value of the range of frequencies used for the frequency response
    timespan = 1/f*3 # initialise time span to three periods of the signal of frequency testf
    command(oscope, f"timebase:scale {timespan/12}") # find time/div by dividing timespan by 12
    g = 10  # initial gain estimate, this will set the vertical range to twice the first pk-pk voltage
    
    # Adjusts time axis
    if timespan > 10*1/f: # if too many periods are shown reduce timespan
        timespan = 1/(f*3)
        command(oscope, f"timebase:scale {timespan/12}") # find time/div by dividing timespan by 12

    # Initial voltage axis adjustment
    command(oscope, f"channel{chan}:SCALE {g*v/10}")
    v_meas = read_measurement(meas_chan)
            
    # Adjusts voltage axis
    while v_meas > (0.85*g*v):   # if the pk-pk output voltage occupies more than 85# of the screen, change volts/div
        g = 1.5*g
        command(oscope, f"channel{chan}:SCALE {g*v/10}")
        v_meas = read_measurement(meas_chan)
            
        if v_meas < 0.3*g*v:  # if the pk-pk output voltage occupies less than 30# of the screen, change volts/div
            g = g/3
            command(oscope, f"channel{chan}:SCALE {g*v/10}")
            v_meas = read_measurement(meas_chan)


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

    time.sleep(0.5)
    if meas_type == 0:
        command(oscope, f"MEASurement{meas_chan}:RESult?")
    else:
        command(oscope, f"MEASurement{meas_chan}:RESult:{meas_type}?")
    time.sleep(0.5) # Time for the oscilloscope to load the result
    value_string = oscope.read()
    value = float(value_string)

    return value


def acquire_waveform(chan):
    """Acquires the waveform by reading each byte individually."""

    command(oscope, 'TIM:SCAL 2E-4')
    command(oscope, f'CHAN{chan}:RANG 15')
    command(oscope, 'FORM BYTE')
    command(oscope, f'CHAN{chan}:DATA:POIN DMAX:')
    #command(oscope, 'SING*;OPC?')
    command(oscope, f'CHAN{chan}:DATA:HEAD?')
    header = str(oscope.read()).split(',')
    X_start = header[0]
    X_stop = header[1]
    num_samples = header[2]
    val_per_samp = header[3]
    command(oscope, f'CHAN{chan}:DATA:YRES?')
    y_res = float(oscope.read())
    command(oscope, f'CHAN{chan}:DATA:XOR?')
    x_or = float(oscope.read())
    command(oscope, f'CHAN{chan}:DATA:XINC?')
    x_inc = float(oscope.read())
    command(oscope, 'FORM WORD')
    time.sleep(0.1)
    command(oscope, f'CHAN{chan}:DATA:YOR?')
    time.sleep(0.1)
    y_or = float(oscope.read())
    command(oscope, f'CHAN{chan}:DATA:YINC?')
    y_inc = float(oscope.read())
    print('y_res', y_res)
    print('y_or' ,y_or)
    print('x_or', x_or) # same as x_start
    print('y_inc', y_inc)
    print('x_inc', x_inc)
    print(header)

    command(oscope, 'FORM:BORD LSBF') # each data point will become a word (i.e. two bytes), the Least Significant Byte (LSB) will come first
    command(oscope, f':DIGitize CHANnel{chan}') # digitise channel, see Appendix (page 89)
    command(oscope, f'CHAN{chan}:DATA?') # request channel data
    bin_size = oscope.baud_rate
    iterations = int(num_samples)/bin_size
    iterations = ceil(iterations)

    data = []
    print('here')
    count = 0
    while count < int(num_samples):
        temp_data = oscope.read_bytes(1)
        data.append(temp_data)
        count+=1
        print(count)

    #print(data)
    #for _ in range(iterations-1):
    #    temp_data = oscope.read_bytes(bin_size/2)
    #    print(temp_data)
    #    data.append(temp_data)
    print('Length=', len(data))
    data_join = b''.join(data)
    ascii_code = []
    for b in data_join:
    #     print(b)
         ascii_code.append(chr(b))
    ascii_code_join = ''.join(ascii_code).split(',')
    ascii_code_join_int = []
    #print(ascii_code_join)
    for i in ascii_code_join:
         ascii_code_join_int.append(float(i))
    print(ascii_code_join_int)
    # print(ascii_code_join_int[0]* float(y_inc) + float(y_or))

    no_of_data_array_elements= len(ascii_code_join_int)

    time_values = []
    voltages = []
    for i in range(no_of_data_array_elements):
        time_values.append((i * float(x_inc)) + float(x_or)) # recreates a vector for the X values using the ‘x_or’ and ‘x_inc’ values acquired from the scope
        voltages.append((ascii_code_join_int[i] * float(y_inc)) + float(y_or)); # recreates the Y values using the ‘y_or’ and ‘y_inc’ values acquired from the scope

    #print(time_values)
    #print(voltages)
    print('success')



    # if method == "byte":
    #     data = oscope.read_bytes(1)
    #     while data != '#':
    #         data = oscope.read_bytes(1)
    #         print(data)
    #     header_len_ascii=oscope.read_bytes(1)
    #     header_len = int(chr(header_len_ascii))
    #     acquired_length = oscope.read_bytes(header_len)
    #     L=int(chr(acquired_length))
    #     print('H_L', header_len)
    #     print ('A_L=',acquired_length)
    #     #bin_size=obj2.InputBufferSize;
    #     #iterations=L/bin_size; # calculate number of bins/iterations
    # #iter_no=ceil(iterations) # round iterations to the next integer
    # #w=1
    # #for k=1:(iter_no-1) # data acquisition loop
    # #temp=fread(obj2,bin_size/2,'int16'); # read the data in the current bin. We are
    # ## reading bin_size/2 elements of type ‘int16’(word). Since
    # ## each ‘int16’ is two bytes long, we are actually reading bin_size bytes.
    # #a(w:w-1+bin_size/2)=temp; # add the elements to the Y data vector, 'a'
    # #w=w+bin_size/2; # increment index for vector 'a'
    # #end
    # #no_of_data_array_elements= max(size(a));

    # #for i=1:1:no_of_data_array_elements
    # ## See Appendix, page 89
    # #time_value(i) =(i * xinc) + xorg; # recreates a vector for the Xvalues
    # ## using the ‘xorg’ and ‘xinc’ values acquired from the scope
    # #volts(i) = ( (a(i) * yinc_num ) + yorg_num ); #recreates a vector
    # ## for the Yvalues

    #elif method == "byte":
    #    byte_count = 0
    #    data_list = []
    #    while byte_count != oscope.baud_rate:
    #        data = oscope.read_bytes(1)
    #        data_list.append(data)
    #        byte_count += 1
    #    waveform = data_list

    return time_values, voltages


def acquire_waveform_W(chan, vinpp, frequency, offset=0.0):
    """Acquire waveform."""

    vin=vinpp/2 # vinpp is the pk-pk amplitude
    timespan=1/(frequency*2)  # initialise time span to two periods of the signal of frequency

    ## OSCILLOSCOPE INITIAL SET-UP 

    # SET BUFFER SIZE

    # SET UP CHANNEL
    command(oscope, 'CHAN1:TYPE HRES')
    command(oscope, 'FORM UINT,16;FORM?')
    form = oscope.read()
    command(oscope, f'TIM:SCAL {timespan}')
    command(oscope, f'CHAN1:RANG {vinpp*10.5}')

    # SET UP INTERNAL SIGNAL GENERATOR
    command(oscope,':WGEN:OUTPut ON')
    command(oscope,f':WGEN:VOLTage {vinpp}')
    command(oscope,f':WGEN:VOLTage:OFFset {offset}')
    command(oscope,f':WGEN:FREQuency {frequency}')

    # SET UP TRIGGER
    command(oscope, f':TRIGger:EDGE:SOURce CHANnel{chan}')
    command(oscope,'TRIGger:MODE EDGE')             
    command(oscope,'TRIGger:SLOpe POSitive')
    command(oscope,'TRIGger:LEVel 0') 

    # RESET SCOPE
    #command(oscope, '*RST')

    # READ HEADER
    command(oscope, f'CHAN{chan}:DATA:HEAD?')
    header = str(oscope.read()).split(',')
    X_start = header[0]
    X_stop = header[1]
    num_samples = header[2]
    val_per_samp = header[3]
    command(oscope, 'SING;*OPC?')
    time.sleep(1)
    opc = oscope.read()
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

    # READ DATA CONVERSION INFO
    command(oscope, f'CHAN{chan}:DATA:POIN DMAX')
    command(oscope, f'CHAN{chan}:DATA:POIN?')
    d_points = oscope.read()
    command(oscope, 'SING;*OPC?')
    opc = oscope.read()
    command(oscope, f'CHAN{chan}:DATA:YRES?')
    yres = oscope.read()
    yres = chr(int(yres))
    command(oscope, f'CHAN{chan}:DATA:YOR?')
    yor = oscope.read()
    command(oscope, f'CHAN{chan}:DATA:XOR?')
    xor = oscope.read()
    command(oscope, f'CHAN{chan}:DATA:XINC?')
    xinc = oscope.read()
    command(oscope, 'FORM UINT,16;FORM?')
    form = oscope.read()
    print(form)
    command(oscope, 'FORM:BORD LSBF')
    command(oscope, f'CHAN{chan}:DATA:YINC?')
    yinc = oscope.read()
    time.sleep(1)
    command(oscope, f'CHAN{chan}:DATA?')
    bin_size = oscope.baud_rate # determine data bin size
    iterations = int(num_samples)/bin_size # calculate number of bins/iterations
    iter_no=ceil(iterations)-1; # round iterations to the next integer
    iter_no *= 2

    # DATA ACQUISITION LOOP
    headerdata= oscope.read_bytes(8) # removes header
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
    times = [i * float(xinc) + float(xor) for i in range(no_of_data_array_elements)]
    voltages = waveform_data * float(yinc) + float(yor) 

    # PLOT WAVEFORM
    plt.plot(times,voltages)
    plt.show()

    # CLOSE INSTRUMENT
    oscope.close()

    return times, voltages

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

# Control Instruments

# Set up oscilloscope
oscope_preset()
oscope_default_settings(1)
#oscope_default_settings(2)

# Set up measurement channels
#measurement_channel_setup(1, 'PEAK', 1)
#measurement_channel_setup(2, 'PEAK', 2)
#measurement_channel_setup(3, 'PHASe', 1, 2)

# Set parameters
Vin_PP = [0.4, 1, 1.5]
Offset = 0.0
Frequencies = [10,100,1000,10000]

# Initiate result variables
#v_in_list = []
#v_out_list = []
#phase_list = []
#results_dict = {} 


# Set up signal generator
oscope_set_siggen(Vin_PP[1],Frequencies[2])
time.sleep(0.5)

# Set up trigger levels
oscope_trigger_settings(1, 0)
time.sleep(0.1)

# Acquire waveform
times, voltages = acquire_waveform_W(1,Vin_PP[1],Frequencies[2])
#print (times)
#print(voltages)
print(len(times), len(voltages))


#yrange_cmd=['channel3:RANGe ' num2str(3*vinpp)];
#command(oscope, f'CHAN1:RANG 500);
#command(oscope,':TRIGger:EDGE:SOURce channel3');
#command(oscope,'TRIGger:MODE EDGE');                 
#command(oscope,'TRIGger:SLOpe POSitive');
#command(oscope,'TRIGger:LEVel 0');
#command(oscope,['TIMEBASE:RANGE ' num2str(timespan)]);



# for v in Vin_PP:
#     for f in Frequencies:
#         oscope_set_siggen(v,f)
#         #auto_adjust(v, f, 1, 1)
#         #auto_adjust(v, f, 2, 2)
#         time.sleep(3) # wait for changes to take effect
#         v_in = read_measurement(1)
#         v_out = read_measurement(2)
#         phase = read_measurement(3)
#         values = acquire_waveform(1)
#         print(values)
#         v_in_list.append(v_in)
#         v_out_list.append(v_out)
#         phase_list.append(phase)
#         results_dict[f"v={v} f={f}"] = (v_in, v_out, phase)

# print(results_dict)
