## UPDATE
# This script is designed to:
# 1. Collate user input
# 2. Preset the oscilloscope
# 3. Adjust the signal generator settings
# 4. Adjust oscilloscope settings
# 5. Send commands to MATLAB to connect to and instruct the oscilloscope

from logging import PlaceHolder
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

def oscope_siggen(volt, freq):
    command(oscope, ":WGENerator:OUTPut:LOAD HIGHz")
    command(oscope, ":WGEN:OUTPut ON")
    for v in volt:
        command(oscope, f":WGEN:VOLTage {v}")
        for f in freq:
            command(oscope, f":WGEN:FREQuency {f}")



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
instruments = (oscope,PlaceHolder)
if quick == 0:
    mmeter = connect_instrument(multimeter1_string)
    psource = connect_instrument(powersupply1_string)
    siggen = connect_instrument(signalgenerator1_string)
    instruments = (oscope, mmeter, psource, siggen)



for instrument in instruments:
    try:
        req_info(instrument)
        print(f"Successfully connected to {instrument}")
    except Exception:
        print(f"Connection to {str(instrument)} failed")

# Control Instruments

oscope_preset()
oscope_default_settings(1)
oscope_default_settings(2)
#V = oscope.read()
#print("V:", V)
#read(oscope, f"MEASurement Vpp RESult:PPEak?")

oscope_siggen((1,10),(1,10,100))

print(voltage_measure(1))
oscope_offset(1, '10000')

# V1 = voltage_measure('1', '1')
#
