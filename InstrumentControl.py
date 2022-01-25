## UPDATE
# This script is designed to:
# 1. Collate user input
# 2. Preset the oscilloscope
# 3. Adjust the signal generator settings
# 4. Adjust oscilloscope settings
# 5. Send commands to MATLAB to connect to and instruct the oscilloscope

import pyvisa
import time

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
    print(info)

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
        instrument.baud_rate = 1000  # Set buffer size to be 1000
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
    idn = instrument.query('*IDN?')
    print(f"\nHello, I am: '{idn}'")


# -------------------------------
# OSCILLOSCOPE COMMANDS
# -------------------------------

def oscope_preset():
    "Resets the oscilloscope"
    command(oscope, '*DCL') # *DCL clears status registers
    command(oscope, '*CLS') # *CLS clears output queue
    command(oscope, '*RST')


def oscope_default_settings(channel='1', coupling='DC', offset='0.0', horizontal_range='5.0'):
    command(oscope, "TIM:ACQT 0.01")  # 10ms Acquisition time
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
    command(oscope, f"TRIG:A:SOUR CH {channel}")  # Trigger source Channel set
    command(oscope, f"TRIG:A:LEV1 {trigger_level}")  # Trigger level set
    oscope.query_opc()


def oscope_set_siggen(v, f, offset=0.0):
    command(oscope, ":WGENerator:OUTPut:LOAD HIGHz")
    command(oscope, ":WGEN:OUTPut ON")
    command(oscope, f":WGEN:VOLTage {v}")
    command(oscope, f":WGEN:VOLTage:OFFset {offset}")
    command(oscope, f":WGEN:FREQuency {f}")


def autoscale(v, f, chan):
    """Autoscales so the waveform always fits the screen"""

    # Initial time axis adjustment
    testf = f # a test frequency, testf, is used to work out the initial settings. testf is set to the first value of the range of frequencies used for the frequency response
    timespan = 1/testf*3 # initialise time span to three periods of the signal of frequency testf
    command(oscope, f"timebase:scale {timespan/12}") # find time/div by dividing timespan by 12
    g = 10  # initial gain estimate, this will set the vertical range to twice the first pk-pk voltage
    
    # Adjusts time axis
    if timespan > 10*1/f: # if too many periods are shown reduce timespan
        timespan = 1/(f*3)
        command(oscope, f"timebase:scale {timespan/12}") # find time/div by dividing timespan by 12

    # Adjusts voltage axis
    command(oscope, f"channel{chan}:SCALE {g*v/10}")
    command(oscope, f"MEAS{chan}:RESult?") # measure pk-pk voltage
    v_meas=fscanf(obj2,'%f')
    #command(oscope, f"MEAS{chan}:RESult?") # measure pk-pk input voltage
    #vinm(i)=fscanf(obj2,'%f')
            
    while v_meas > (0.85*g*v):   # if the pk-pk output voltage occupies more than 85% of the screen, change volts/div
        g = 1.5*g
        command(oscope, f"channel{chan}:SCALE {g*v/10}")
        #pause(0.5)
        command(oscope, f"MEAS{chan}:RESult?") # measure pk-pk voltage
        v_meas = fscanf(obj2,'%f')
            
        if v_meas < 0.3*g*v:  # if the pk-pk output voltage occupies less than 30% of the screen, change volts/div
            g = g/3
            command(oscope, f"channel{chan}:SCALE {g*v/10}")
            #pause(0.5)
            command(oscope, f"MEAS{chan}:RESult?") # measure pk-pk voltage
            v_meas = fscanf(obj2,'%f')

def voltage_measure(channel, meas_chan=1, main='PEAK'):  # can change main to choose PEAK, MEAN, RMS, etc.
    """Measures voltage"""

    command(oscope, f"MEASurement {meas_chan} :ON")
    command(oscope, f"MEASurement {meas_chan} :SOURce CH {channel}")
    command(oscope, f"MEASurement {meas_chan} :MAIN {main}")
    command(oscope, f"MEASurement {meas_chan} STATitics ON")
    command(oscope, f"MEASurement {meas_chan} STATitics RESet")
    time.sleep(0.3)  # Wait for stats to be reset and for a few values to be taken
    # V_string = read(oscope, f"MEASurement {type} RESult:PPEak?")
    command(oscope, f"MEASurement {meas_chan} RESult:AVG?") # Request voltage
    # command('MEASurement' + measurement + ':RESult:PPEak?')
    time.sleep(0.75)
    V_string = oscope.read()
    V = float(V_string)

    # CHECK If fails trying changing type to 1,2,3,4 or Vpp etc

    return V


def phase_measure(channel_1, channel_2, meas_chan=1):
    """Measures the phase difference between two channel"""

    command(oscope, f"MEASurement {meas_chan} :ON")
    command(oscope, f"MEASurement {meas_chan} :SOURce CH{channel_1},CH{channel_2}") # Set sources to be chosen channels
    command(oscope, f"MEASurement {meas_chan} :MAIN PHASe")
    command(oscope, f"MEASurement {meas_chan} STATitics ON")
    command(oscope, f"MEASurement {meas_chan} STATitics RESet")
    time.sleep(0.3)  # Wait for stats to be reset and for a few values to be taken
    #command(oscope, f"MEASurement {meas_chan} RESult:PPEak?") # Request phase difference
    command(oscope, f"MEASurement {meas_chan} RESult:AVG?") # Request phase difference
    phase_string = oscope.read()
    phase = float(phase_string)

    # CHECK

    # If statements to detect an invalid output from instrument which can occur if the voltage is very low (1mV)
    if phase > 180:
        phase = None  # None is value that can be recorded in a list but will not display on a plot
    elif phase < -180:
        phase = None

    return phase


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

Vin_PP = [0.4]
Offset = 0.0
Frequencies = [1,10,100,1000]

oscope_preset()
oscope_default_settings(1)
oscope_default_settings(2)

for v in Vin_PP:
    command(oscope, f":WGEN:VOLTage {v}")
    command(oscope, f":WGEN:VOLTage:OFFset {Offset}")
    for f in Frequencies:
        oscope_set_siggen(v,f)
        #autoscale(v, f)
        time.sleep(0.5) # wait for changes to take effect
        #command(oscope, "SINGle") # take a measurement

#V = oscope.read()
#print("V:", V)
#read(oscope, f"MEASurement Vpp RESult:PPEak?")

#print(voltage_measure(1))
#oscope_offset(1, '10000')

# V1 = voltage_measure('1', '1')
#
