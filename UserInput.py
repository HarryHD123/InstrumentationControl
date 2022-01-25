
# This script is designed to:
# 1. Ask for the user to input variables required for to control the instruments
# 2. Convert that input into a usable format to be sent to setup.py

VoltageUp = input("Enter the upper voltage \n")
VoltageLow = input("Enter the lower voltage \n")

FreqUp = input("Enter the upper frequency \n")
FreqLow = input("Enter the lower frequency \n")

print("Measuring for a voltage range of", VoltageLow, "to", VoltageUp)
print("Measuring for a frequency range of", FreqLow, "to", FreqUp)


UserSettings = (VoltageUp, VoltageLow, FreqUp, FreqLow)
