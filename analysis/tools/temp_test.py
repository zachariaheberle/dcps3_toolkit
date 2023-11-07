import pyvisa

rm = pyvisa.ResourceManager()

inst = rm.open_resource("ASRL1::INSTR")
inst.baud_rate = 38400
print(inst.query("MEAS:TEMP? RTD,(@102)"))