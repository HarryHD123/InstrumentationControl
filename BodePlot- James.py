import pyvisa
#import matplotlib.pyplot as plt  # For plotting
import numpy as np
import time  # To implement sleep/pause functionality
import math  # For log

# The objective of this code is to, through MATLAB and communication with
# a physical instrument, produce a [Bode] plot that plots the transfer
# function of a filter over a large range of frequencies.
# This code was intended for use with the Rohde and Schwarz RTB2004.
# This code REQUIRES Keysight IO suite to be installed and to have the instrument set up on it
# This code requires pyvisa which is not a part of the default. It can be installed through the Project Interpreter
# on Pycharm

# This is the Python version of a MATLAB code under the same name. As a result, this code has been 'translated'
# from MATLAB to Python. This version is slightly outdated compared to the MATLAB version.

# For brevity, the structural  differences between Python and MATLAB will not be explained in this code,
# but it is important to explain some of the differences between the Python module that we are using (pyvisa)
# compared to using Instrumentation Control on MATLAB.

# 1. pyvisa has no GUI or method to see your instrumentation. Instead you have to do setup via console or code,
# using the commands below.

# 2. To print to an instrument in pyvisa you must use print(obj1.write). To read you must use x = obj1.read()

# 3. Pyvisa is significantly slower at reading results than MATLAB. You almost always need some delay when a read
# command is sent

# 4. It's worth mentioning that strings are quite different between MATLAB and Python. For example, to concatenate
# a string in Python you simply use ('Hello '+'World')



rm = pyvisa.ResourceManager()  # Setup resource manager
# rm.list_resources()  # Use this command to display available instruments
obj1 = rm.open_resource('TCPIP0::192.168.1.2::inst0::INSTR')  # Set oscilloscope to obj1
obj1.read_termination = '\n'  # Define the last line of an input to be a paragraph break (which is what the instrument sends)
obj1.write_termination = ''  # Set the output (to the instrument) to be whatever message is included within a string
obj1.baud_rate = 1000  # Set buffer size to be 1000

print(obj1.query('*IDN?'))

# obj1.query_delay = 5  # Add a 5ms delay between a write and read - query command not utilised in this code


# Functions (have to be defined after the initial set up to work)
def setyScale(obj1):  # Function for automatically scaling the y axis on the instrument sceen so that the waveform
    # automatically takes up 70% of the screen so that accurate measurements can be taken and there is no clipping

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
    print(obj1.write('CHANnel1:RANGe ' + str(newrange)))  # Reshape waveform so the waveform takes up half the screen
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

    # # Clipping detection and auto y scale for channel 2, same as channel 1
    print(obj1.write('CHANnel2:RANGe 79'))  # Zoom out as far as possible to take a rough measurement
    print(obj1.write('DVM:SOUR CH2'))  # Set source to channel 1
    print(obj1.write('DVM:TYPE ACDC'))  # Set type to AC + DC
    print(obj1.write('DVM:RES:STAT?'))  # Request a voltage level
    result = obj1.read()
    result = result.split(',')
    newrange = (4 / 0.707) * float(result[0])
    print(obj1.write('CHANnel2:RANGe ' + str(newrange)))  # Reshape waveform so the waveform takes up half the screen
    print(obj1.write('TRIGger:A:SOURce CH2'))  # use the modulating waveform on CH2 as a trigger
    print(obj1.write('TRIGger:A:TYPE EDGE'))
    print(obj1.write('TRIGger:A:EDGE:SLOpe POSitive'))
    print(obj1.write('TRIGger:A:LEVel ' + str(newrange / 30)))  # set the trigger
    print(obj1.write('DVM:RES:STAT?'))  # Take a new voltage measurement that is more accurate than the previous one
    result2 = obj1.read()
    result2 = result2.split(',')
    newrange2 = (2 / 0.707) * 1.3 * float(result2[0])
    print(obj1.write('CHANnel2:RANGe ' + str(newrange2)))  # Reshape waveform so it takes up 70% of the screen
    print(obj1.write('DVM:RES:STAT?'))  # Check for clipping
    clippingCheck = obj1.read()
    clippingCheck = clippingCheck.split(',')
    # Clippingcheck will be = 1 if there is no clipping
    if clippingCheck[1] != 1:  # If there is clipping
        clipping = 'TRUE'
        print(obj1.write('CHAN2:BAND B20'))  # Limit the bandwidth to produce a cleaner picture
        print(obj1.write('DVM:RES:STAT?'))
        clippingCheck = obj1.read()
    else:
        clipping = 'FALSE'


def phaseDifference(obj1):  # function to take an average phase difference measurement
    print(obj1.write('MEASurement1:ON'))
    print(obj1.write('MEASurement1:SOURce CH2,CH1'))  # Set sources to be C2-C1
    print(obj1.write('MEASurement1:MAIN PHASe'))
    print(obj1.write('MEASurement1:STATistics ON'))
    print(obj1.write('MEASurement1:STATistics RESet'))  # Reset stats
    time.sleep(0.3)  # Wait for stats to be reset and for a few values to be taken
    print(obj1.write('MEASurement1:RESult:AVG?'))
    time.sleep(0.75)
    phaseDiffString = obj1.read()
    phase = float(phaseDiffString)
    # If statements to detect an invalid output from instrument which can occur if the voltage is very low (1mV)
    if phase > 180:
        phase = None  # None is value that can be recorded in a list but will not display on a plot
    elif phase < -180:
        phase = None
    return phase


def measureVolts(obj1):  # function to measure average peak to peak voltages
    # Measure Vin
    print(obj1.write('MEASurement2:ON'))
    print(obj1.write('MEASurement2:SOURce CH1'))  # Measure channel 1
    print(obj1.write('MEASurement2:MAIN PEAK'))
    print(obj1.write('MEASurement2:STATistics ON'))
    print(obj1.write('MEASurement2:STATistics RESet'))
    time.sleep(0.3)  # Wait for stats to be reset and for a few values to be taken
    print(obj1.write('MEASurement2:RESult:AVG?'))
    time.sleep(0.75)
    VInString = obj1.read()  # Record V In
    VpIn = float(VInString)
    # Measure Vout
    print(obj1.write('MEASurement3:ON'))
    print(obj1.write('MEASurement3:SOURce CH2'))
    print(obj1.write('MEASurement3:MAIN PEAK'))
    print(obj1.write('MEASurement3:STATistics ON'))
    print(obj1.write('MEASurement3:STATistics RESet'))
    print(obj1.write('MEASurement3:RESult:AVG?'))
    time.sleep(0.75)
    VOutString = obj1.read()
    VpOut = float(VOutString)

    return [VpOut, VpIn]


# Instrument Configuration and Control
# # Setup

print(obj1.write('*RST'))  # reset scope
print(obj1.write('CHANnel1:TYPE HRES'))  # Set to high res
print(obj1.write('CHANnel3:STAT OFF'))  # turn off Channel 3 and 4
print(obj1.write('CHANnel4:STAT OFF'))
print(obj1.write('CHANnel1:STAT ON'))  # turn on Channel 1 for output
print(obj1.write('CHANnel2:STAT ON'))  # turn on Channel 2 for input (measurement)
print(obj1.write('*DCL'))  # *DCL and *CLS clear status registers and output queue
print(obj1.write('*CLS'))
#print(obj1.write(':WGENerator:OUTPut:LOAD HIGHz'))
print(obj1.write(':WGEN:OUTPut ON'))  # Turn on output of waveform generator
print(obj1.write('CHAN1:OFFset 0'))  # ensure the offset on CH1 is zero

# # Obtaining Data
freqMax = 6  # 6 = 10 ^ 6 = 1000000
freqMin = 3  # 3 = 10 ^ 3 = 1000
freqs = np.logspace(freqMin, freqMax, 10)  # Create a log space list of frequencies
voltage = 10  # Voltage set to 5 V peak to peak
print(obj1.write(':WGEN:VOLTage ' + str(10)))
phaseDiffList = []
print(obj1.write(':WGEN:FREQuency ' + str(freqs[0])))
[VppOut, VppIn] = measureVolts(obj1)

#Set starting values for variables in for loop
grad = 0
H = 0
freqVal = 0
H_amp = []
printFreqs = []


for i in freqs:  # Iterate through every frequency and record values for each frequency
    print(obj1.write(':WGEN:FREQuency ' + str(i)))  # Set the current frequency
    time.sleep(0.25)
    timespan = 1 / i * 3
    print(obj1.write('timebase:scale ' + str(timespan / 12)))  # Set timescale of oscilloscope
    setyScale(obj1)
    time.sleep(0.25)
    [VppOut, VppIn] = measureVolts(obj1)

    # Set current and previous values for use in  auto-measuring algorithm
    prev_H = H
    H = VppOut / VppIn
    nextH = H
    prevFreqVal = freqVal
    freqVal = 10 * math.log10(i)
    prevGrad = grad
    grad = (prev_H - H) / (prevFreqVal - freqVal)
    phaseDiff = phaseDifference(obj1)
    nextPhaseDiff = phaseDiff

    print(grad)
    if abs(grad) > 0.02 or np.sign(prevGrad) != np.sign(grad):  # Does extra data points if there is a steep gradient
        sensitivity = 60  # Gradient varies between 0.01 and 0.1. Sensitivity determines how many extra points are
        # measured when the gradient is steep. A value of 50 will produce 5 extra data points when the gradient
        # is at its steepest
        numberOfPoints = int(sensitivity * abs(grad))  # Determine the number of extra points to be plottedm

        for x in range(numberOfPoints-1):  # Loop through every point and plot
            newFreqVal = ((freqVal - prevFreqVal) * (x + 1) / numberOfPoints) + prevFreqVal
            newFreq = 10 ** (newFreqVal / 10)  # Calculate new frequency to be added and measured
            printFreqs.append(newFreq)
            print(obj1.write(':WGEN:FREQuency ' + str(newFreq)))
            time.sleep(0.25)
            timespan = 1 / newFreq * 3
            print(obj1.write('timebase:scale ' + str(timespan / 12)))  # Set timescale of instrument to display 3 waves
            setyScale(obj1)  # Auto-scale y axis
            [VppOut, VppIn] = measureVolts(obj1)  # measure voltage
            phaseDiff = phaseDifference(obj1)  # measure phase difference
            phaseDiffList.append(phaseDiff)  # add to appropriate list
            H = VppOut / VppIn
            H_amp.append(H)

    printFreqs.append(i)  # Record the final frequency
    phaseDiffList.append(nextPhaseDiff)
    H_amp.append(nextH)

# Transfer function
H_amp_dB = [20 * math.log10(element) for element in H_amp]  # Convert transfer function to dB


# Plot magnitude of transfer function in dB
plt.figure(1)  # Set figure 1
plt.semilogx(printFreqs, H_amp_dB)  # Plot
plt.xlabel('Frequency (Hz)')
plt.ylabel('dB')
plt.title('Magnitude of the transfer function in dB')
plt.grid()

# Plot phase difference
plt.figure(2)  # Set figure 2
plt.semilogx(printFreqs, phaseDiffList) # Plot
plt.xlabel('Frequency (Hz)')
plt.ylabel('deg')
plt.title('Phase of the transfer function in degrees')
plt.grid()

plt.show()  # Show all plots

