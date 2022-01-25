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

"""
def set_scale_auto(channel):
  ""Automatically scales the y axis on the oscilloscope.
    This is so accurate measurements can be taken and clipping is prevented""

    # Zoom out as far as possible to take a rough measurement
    print(obj1.write('CHAN1nel:RANGe 79'))
    print(obj1.write('DVM:ENAB ON'))  # DVM - digital voltmeter for measuring the voltages
    print(obj1.write('DVM:SOUR CH1'))  # Set source to channel 1
    print(obj1.write('DVM:TYPE ACDC'))  # Set type to AC + DC
    print(obj1.write('DVM:RES:STAT?'))  # Request a voltage level
    time.sleep(0.75)  # Add some delay to give the scope time to process the request
    result = obj1.read()  # Read result which is a string separated by commas
    time.sleep(0.2)
    result = result.split(',')  # Split result by comma
    # result[0] is the rms voltage as a string
    newrange = (4 / 0.707) * float(result[0])  # convert result to a float and set new range for y axis

    # Resize again and take a more accurate measurement
    print(
        obj1.write('CHANnel1:RANGe ' + str(newrange)))  # Reshape waveform so the waveform takes up half the screen
    print(obj1.write('TRIGger:A:SOURce CH1'))  # use the modulating waveform on ch1 as a trigger
    print(obj1.write('TRIGger:A:TYPE EDGE'))  # Set positive edge trigger
    print(obj1.write('TRIGger:A:EDGE:SLOpe POSitive'))
    print(obj1.write('TRIGger:A:LEVel ' + str(newrange / 30)))  # set the trigger to a small non-zero value
    print(obj1.write('DVM:RES:STAT?'))  # Take a new voltage measurement that is more accurate than the previous one
    time.sleep(0.75)
    result2 = obj1.read()
    result2 = result2.split(',')
    newrange2 = (2 / 0.707) * 1.3 * float(result2[0])

    # Resize again so that waveform takes up 70% of screen
    print(obj1.write('CHANnel1:RANGe ' + str(newrange2)))  # Reshape waveform so it takes up 70% of the screen
    print(obj1.write('DVM:RES:STAT?'))  # Check for clipping
    clippingCheck = obj1.read()
    clippingCheck = clippingCheck.split(',')
    # Clippingcheck will be = 1 if there is no clipping
    if clippingCheck[1] != 1:  # If there is clipping...
        clipping = 'TRUE'
        print(obj1.write('CHAN1:BAND B20'))  # Limit the bandwidth to produce a cleaner picture
        print(obj1.write('DVM:RES:STAT?'))  # Take another measurement
        clippingCheck = obj1.read()
        clippingCheck = clippingCheck.split(',')
    else:
        clipping = 'FALSE'
    """

    """
    %% Keysight scope
fprintf(obj2,['timebase:scale ' num2str(timespan/12)])  %find time/div by dividing timespan by 12

fprintf(obj2,['MEAS1:Enable ON'])
fprintf(obj2,['MEAS1:Source ch2'])
fprintf(obj2,['MEAS1:MAIN PEAK']);

fprintf(obj2,['MEAS2:Enable ON'])
fprintf(obj2,['MEAS2:Source ch1'])
fprintf(obj2,['MEAS2:MAIN PEAK']);

timespank=timespan;

g=10  % initial gain estimate, the will set the vertical range to twice the pk-pk voltage

for i=1:length(frange)
    

    
    fprintf(obj2,[':WGEN:FREQuency ' num2str(frange(i))])  %set sig gen frequency
%     if i<12
%     pause(0.5)
%     end
    %fprintf(obj2,'SINGLE');
    
if timespan>10*1/frange(i)      %if too many periods are shown reduce timespan
    timespan=1/frange(i)*3
    fprintf(obj2,['timebase:scale ' num2str(timespan/12)])
    end

yrange_cmd=['channel2:SCALE ' num2str(g*vinpp/10)] 
fprintf(obj2,yrange_cmd);
fprintf(obj2,'MEAS1:RESult?')     %measure pk-pk output voltage
vppk(i)=fscanf(obj2,'%f')
fprintf(obj2,'MEAS2:RESult?')     %measure pk-pk input voltage
vinm(i)=fscanf(obj2,'%f')
        
        while vppk(i) > (0.85*g*vinpp)   %if the pk-pk output voltage occupies more than 85% of the screen, change volts/div
            g=1.5*g
            yrange_cmd=['channel2:SCALE ' num2str(g*vinpp/10)]
            fprintf(obj2,yrange_cmd);
            pause(0.5)
            fprintf(obj2,'MEAS1:RESult?')
            vppk(i)=fscanf(obj2,'%f')
        end
        
    if vppk(i)<0.3*g*vinpp  %if the pk-pk output voltage occupies less than 30% of the screen, change volts/div
        g=g/3
        yrange_cmd=['channel2:SCALE ' num2str(g*vinpp/10)]
        fprintf(obj2,yrange_cmd);
        pause(0.5)
        fprintf(obj2,'MEAS1:RESult?')
        vppk(i)=fscanf(obj2,'%f')
    end   
        
end


fprintf(obj2,':WGEN:OUTPut OFF') % turn off sig gen


gaink=20*log10(vppk./vinm);
"""

# -------------------------------
# RECORD MEASUREMENTS FROM THE OSCILLOSCOPE
# -------------------------------

# Main

# Connect to Instruments

oscope = connect_instrument(oscilloscope1_string)
mmeter = connect_instrument(multimeter1_string)
psource = connect_instrument(powersupply1_string)
siggen = connect_instrument(signalgenerator1_string)

instruments = (oscope, mmeter, psource, siggen)

for instrument in instruments:
    try:
        req_info(instrument)
        print(f"Successfully connected to {instrument}")
    except Exception:
        print(f"Connection to {instrument} failed")

oscope_preset()
oscope_default_settings(1)
oscope_default_settings(2)
V = oscope.read()
print("V:", V)
read(oscope, f"MEASurement Vpp RESult:PPEak?")
voltage_measure(1)
oscope_offset(1, '10000')

# V1 = voltage_measure('1', '1')
#
