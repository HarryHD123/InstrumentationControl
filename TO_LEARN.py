

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
