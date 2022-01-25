"""
def set_scale_auto(channel):
  """Automatically scales the y axis on the oscilloscope.
    This is so accurate measurements can be taken and clipping is prevented"""

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








# completely deconstruct and learn
def log():
    """Define and begin logging for all 6 set measurements (on 1st screen).
	Also check the directory if the file exists after logging process is complete."""

    try:  # Delete the logfile (if already existing) and
        HMC8015.write_str_with_opc(f'DATA:DELETE "{log_file_name}",EXT')  # insert a try block to prevent throwing an
    except StatusException:  # error when the log file to be deleted is
        pass  # not present

    HMC8015.write_int_with_opc('LOG:PAGE ',
                               pagenum)  # The defined page (pagenum) will be used for logging (is default value, just to show)
    HMC8015.write_str_with_opc('LOG:MODE DURation')  # Log mode is set to a dedicated time
    HMC8015.write_int_with_opc('LOG:DURation ', logdur)  # Set dedicated time (lodur) in seconds for logging duration
    HMC8015.write_str_with_opc('LOG:INTerval MIN')  # Change the logging interval to minimum (100ms)
    HMC8015.write_str_with_opc(
        f'LOG:FNAME "{log_file_name}",EXT')  # Define name (log_file_name) and location for the log file
    HMC8015.write_str_with_opc('LOG:STATe ON')  # Now start logging
    sleep(int(logdur))  # Wait for the log to be written
    file_response = HMC8015.query_str('DATA:LIST? EXT')  # Read out directory content
    print(file_response)


def fileget():
    """Transfer the log file to the local PC"""

    HMC8015.data_chunk_size = 10000  # Define Chunk size (helps with bigger files)
    append = False
    pc_file_path = r'c:\temp\logdata.csv'
    print('Transferring the log file...')
    HMC8015.query_bin_block_to_file(f'DATA:DATA? "{log_file_name}",EXT', pc_file_path,
                                    append)  # Directly stream the file to local PC
    print(f'File saved to {pc_file_path}')
    HMC8015.write_str_with_opc(f'DATA:DELETE "{log_file_name}",EXT')  # Delete the log file after completion
