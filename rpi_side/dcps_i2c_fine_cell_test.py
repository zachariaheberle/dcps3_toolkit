import os
import sys
import time
import digitalio
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_tca9548a
from micropython import const
from microcontroller import Pin
from pca9575_lib import *
# from pca9545a_lib import *

#Do not adjust by hand, use run_dcps_control script
FINE_CONTROL=
COARSE_CONTROL=
STAGE4_TUNE=
STAGE5_TUNE=
CHANNEL=


def get_dcps3packet(fstep, cstep,tuningbits_stage4 = 0b10,tuningbits_stage5 = 0b10):
    i2c_array = [0]*160
    cstep_inverted = (~cstep)&31 #Inverting for Inductor L
    # Coarse Delay
    # Expects it from 0 to 255
    # print(bin(cstep))
    # print(bin((~cstep)&31))

    # Stage 1
    bit_pointer = 0
    i2c_array[bit_pointer   ] = (cstep>>bit_pointer)&0b1            #C_bit Line 1
    i2c_array[bit_pointer+9 ] = ((cstep_inverted>>bit_pointer)&0b1) #L_bit Line 1


    # Stage 2
    bit_pointer = 1
    i2c_array[bit_pointer   ] = (cstep>>bit_pointer)&0b1            #C_bit Line 1
    i2c_array[bit_pointer+9 ] = ((cstep_inverted>>bit_pointer)&0b1) #L_bit Line 1


    # Stage 3
    bit_pointer = 2
    i2c_array[bit_pointer   ] = (cstep>>bit_pointer)&0b1            #C_bit Line 1
    i2c_array[bit_pointer+9 ] = ((cstep_inverted>>bit_pointer)&0b1) #L_bit Line 1


    # Stage 4
    bit_pointer = 3
    i2c_array[bit_pointer     ] = (cstep>>bit_pointer)&0b1            #C_bit Line 1
    #Tuning Bits
    i2c_array[bit_pointer +1  ] = ((tuningbits_stage4)&0b1)&((cstep>>bit_pointer)&0b1)              #C_bit Line 1
    i2c_array[bit_pointer +2  ] = ((tuningbits_stage4>>1)&0b1)&((cstep>>bit_pointer)&0b1)           #C_bit Line 1
    i2c_array[bit_pointer+9   ] = ((cstep_inverted>>bit_pointer)&0b1) #L_bit Line 1

    # Stage 5
    bit_pointer = 4
    i2c_array[bit_pointer+2   ] = (cstep>>bit_pointer)&0b1              #C_bit Line 1
    #Tuning Bits
    i2c_array[bit_pointer+2 +1  ] = ((tuningbits_stage5)&0b1 )&((cstep>>bit_pointer)&0b1)            #C_bit Line 1
    i2c_array[bit_pointer+2 +2  ] = ((tuningbits_stage5>>1)&0b1)&((cstep>>bit_pointer)&0b1)          #C_bit Line 1
    i2c_array[bit_pointer+9 +2] = ((cstep_inverted>>bit_pointer)&0b1)   #L_bit Line 1

    # Copy over configuration for Line 2
    i2c_array[14:28] = i2c_array[0:14]

    # # Print Course Delay Stage
    # print(f"{cstep:05b}")
    # print(f"{cstep_inverted:05b}")
    # enu = 0
    # for i,j in zip(i2c_array[:14],i2c_array[14:28]):
    #     print(f"{enu:03}",':',i,':',j,':',f"{enu+14:03}")
    #     enu=enu+1

    #Fine Delay Stage
    for i in range(66):
        if i == fstep - 1:
            # C bit
            i2c_array[i + 28] = 1
            # L bit
            i2c_array[i + 94] = 0
        else:
            # C bit
            i2c_array[i + 28] = 0
            # L bit
            i2c_array[i + 94] = 1


    # Print Fine Delay Stage
    # print(f"{fstep:05b}")
    # enu = 28
    # for i,j in zip(i2c_array[28:94],i2c_array[94:160]):
    #     print(f"{enu:03}",':',i,':',j,':',f"{enu+66:03}")
    #     enu=enu+1

    # Get as bytes array...
    out_byte_array = bytearray()
    i=0
    # print()




    out_byte_array.append(0) # Set the starting address to zero
    out_byte_array.append(0) # Set the starting address to zero

    for i in range(0,160,8):
        out_byte_array.append(int("".join([str(x) for x in reversed(i2c_array[i:i+8])]),2)) #Correct Order
        # out_byte_array.append(int("".join([str(x) for x in i2c_array[i:i+8]]),2))

    #pad the rest for the registers...
    # for i in range(12): #Ideally should be 12 for some reason, the number that works is 6
    #     out_byte_array.append(0)

    # print(f"\t {cstep:05b}")
    # print(f"\t {cstep_inverted:05b}")
    # for enum, i in enumerate(out_byte_array):
        # print(f"{enum+1:02} : {i:08b}") # Print as Binary
        # print(f"{enum+1:02} : {i:03}") # Print as Int
        # print(f"{enum+1:02} : {i:02x}") # Print as Int Hex

    return out_byte_array #Correct Order
    # return bytearray(reversed(out_byte_array))



# get_dcps3packet(5,0b11010)
# get_dcps3packet(0,0)


# def dcps3(fstep, cstep):
#     i2c_array = [0]*160
    
#     for i in range(5):
#         val = 1&(cstep>>i)
      
#         if i <= 2:
#             # Line 1
#             i2c_array[i] = val
#             # Line 2
#             i2c_array[i + 14] = val
        
#         if i == 3:
#             # Line 1
#             i2c_array[i] = val
#             i2c_array[i + 1] = val
#             i2c_array[i + 2] = val
#             # Line 2
#             i2c_array[i + 14] = val
#             i2c_array[i + 15] = val
#             i2c_array[i + 16] = val
        
#         if i == 4:
#             # Line 1
#             i2c_array[i + 2] = val
#             i2c_array[i + 3] = val
#             i2c_array[i + 4] = val
#             # Line 2
#             i2c_array[i + 16] = val
#             i2c_array[i + 17] = val
#             i2c_array[i + 18] = val
            
#         i2c_array[i + 9] = 0b1&~(val)
#         i2c_array[i + 23] = 0b1&~(val)
    
#     for i in range(66):
#         if i < fstep:
#             # C bit
#             i2c_array[i + 28] = 1
#             # L bit
#             i2c_array[i + 94] = 0
            
#         else:
#             # C bit
#             i2c_array[i + 28] = 0
#             # L bit
#             i2c_array[i + 94] = 1
    
#     # print(i2c_array)
    
#     return convert_ba(i2c_array)  

DELAY_I2C = 0.001
# class i2c_hacked():
#     def __init__(self, sda, scl):
#         """
#         i2c without ack returned...
#         sda --> pin for sda
#         scl --> pin for scl
#         """
#         self.sda = sda
#         self.scl = scl
#         self.sda.value = 1 #Initial Value
#         self.scl.value = 1 #Initial Value

#     def send_bit_one(self):
#         self.scl.value = 0
#         self.sda.value = 1
#         time.sleep(DELAY_I2C)
#         self.scl.value = 1
#         # time.sleep(DELAY_I2C)
#         # self.scl.value = 0
#         # self.sda.value = 0


#     def send_bit_zero(self):
#         self.scl.value = 0
#         self.sda.value = 0
#         time.sleep(DELAY_I2C)
#         self.scl.value = 1
#         # time.sleep(DELAY_I2C)
#         # self.scl.value = 0
#         # self.sda.value = 1


#     def start_comms(self):
#         self.scl.value = 1
#         time.sleep(DELAY_I2C)
#         self.sda.value = 0
        
#         pass

#     def stop_comms(self):
#         self.scl.value = 1
#         self.sda.value = 0
#         time.sleep(DELAY_I2C)
#         self.sda.value = 1
#         pass

#     def choose_high_low(self,i):
#         if i==0:
#             self.send_bit_zero()
#         else:
#             self.send_bit_one()

#     def get_ack(self):
#         self.scl.value = 0
#         self.sda.direction  = digitalio.Direction.INPUT
#         time.sleep(DELAY_I2C)
#         self.scl.value = 1
#         time.sleep(DELAY_I2C)
#         self.scl.value = 0
#         self.sda.direction  = digitalio.Direction.OUTPUT


#     def send_addr_byte_write(self, addr):
#         self.start_comms() #Send StartBit
#         # print(bin(addr))
#         addr = (((0b0111_1111) & (addr)) << 1) | 0b0 
#         # print(bin(addr))
#         time.sleep(DELAY_I2C)
#         for i in [7,6,5,4,3,2,1,0]:
#             # print((addr>>i)&0b1)
#             self.choose_high_low((addr>>i)&0b1)
#             time.sleep(DELAY_I2C)
#         self.get_ack() #Ackowledge bit; Set SDA to be an input
#         # self.send_bit_zero() #Ackowledge bit when slave is supposed to respond
#         time.sleep(DELAY_I2C)

#     def send_addr_byte_read(self, addr):
#         self.start_comms() #Send StartBit
#         addr = (((0b0111_1111) & (addr)) << 1) | 0b1 
#         time.sleep(DELAY_I2C)
#         for i in [7,6,5,4,3,2,1,0]:
#             self.choose_high_low((addr>>i)&0b1)
#             time.sleep(DELAY_I2C)
#         self.get_ack() #Ackowledge bit; Set SDA to be an input
#         # self.send_bit_zero() #Ackowledge bit when slave is supposed to respond
#         time.sleep(DELAY_I2C)

       

#     def send_byte(self, value):
#         time.sleep(DELAY_I2C)
#         for i in [7,6,5,4,3,2,1,0]:
#             self.choose_high_low((value>>i)&0b1)
#             time.sleep(DELAY_I2C)
#         # self.send_bit_zero() #Ackowledge bit when slave is supposed to respond
#         self.get_ack() #Ackowledge bit; Set SDA to be an input
#         time.sleep(DELAY_I2C)


#     def write(self,addr,data_bytes):
#         self.send_addr_byte_write(addr)
#         for data_byte in data_bytes:
#             self.send_byte(data_byte)
#         self.stop_comms()

#     def read(self,addr,data_bytes):
#         self.send_addr_byte_read(addr)
#         for data_byte in data_bytes:
#             self.send_byte(data_byte)
#         self.stop_comms()
#         # pass

def select_mux_channel(ch=2): 
    '''
        Sets the channel for the mux 
        choice 0,1,2,3
        choose 2 where the SDAout is severed from SDAin
    '''
    ch_map = {
        0:0b0001,
        1:0b0010,
        2:0b0100,
        3:0b1000
    }
    i2c.try_lock()
    # i2c.writeto(0x71,bytearray(ch_map[ch]))
    i2c.writeto( 0x71,bytes([ch_map[ch]]) )
    # result = bytearray(1)
    # i2c.readfrom_into(0x71, result)
    # print(result)
    i2c.unlock()



# print(os.uname())
print("Board Name: ",board.board_id)

LED = digitalio.DigitalInOut(board.D13)
CLK_ENB = digitalio.DigitalInOut(board.D11)
CLK_ALT = digitalio.DigitalInOut(board.D10)
RSTB = digitalio.DigitalInOut(board.D12)

LED.direction = digitalio.Direction.OUTPUT
CLK_ENB.direction = digitalio.Direction.OUTPUT
CLK_ALT.direction = digitalio.Direction.OUTPUT
RSTB.direction = digitalio.Direction.OUTPUT


CLK_ENB.value = False
LED.value = True

for i in range(1):
    RSTB.value = False
    time.sleep(1)
    RSTB.value = True
    time.sleep(1)




i2c = busio.I2C(board.SCL, board.SDA)
select_mux_channel(2)
i2c.deinit()
# # i2c.try_lock()
# # print(hex(i2c.scan()[0]))
# # i2c.unlock()




# time.sleep(1)








# for i in dcps3(FINE_CONTROL,COARSE_CONTROL):
#     print(bin(i))


# i2c_SCL = digitalio.DigitalInOut(board.SCL)
# i2c_SDA = digitalio.DigitalInOut(board.SDA)
# i2c_SCL.direction  = digitalio.Direction.OUTPUT
# i2c_SDA.direction  = digitalio.Direction.OUTPUT
# i2c_SDA.value = 1
# i2c_SCL.value = 1

# time.sleep(1)
# i2c_dcpsch2 = i2c_hacked(i2c_SDA, i2c_SCL)
# # i2c_dcpsch2.write(0x70,[])


# # # for i in dcps3(FINE_CONTROL,COARSE_CONTROL):
# #     # print(hex(i))
# i2c_dcpsch2.write(0x70,dcps3(FINE_CONTROL,COARSE_CONTROL))
# # # i2c_dcpsch2.read(0x70,[0x1,0xFF])

# # # #GPIO stuff...
# # # i2c_dcpsch2.write(0x20,bytes([0b00001001,0b1111_0000])) #Turn LED to output
# # # i2c_dcpsch2.write(0x20,bytes([11,0b1111_1110])) #Turn LED to HIGH 


# i2c_SDA.deinit()
# i2c_SCL.deinit()



# time.sleep(1)
i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
i2c.try_lock()
print("FINE_CONTROL:",FINE_CONTROL)
print("COARSE_CONTROL:",COARSE_CONTROL)
print(f"STAGE4_TUNE: {STAGE4_TUNE&0b11:02b}")
print(f"STAGE5_TUNE: {STAGE5_TUNE&0b11:02b}")
print("CHANNEL:", CHANNEL)


#for i in range(300):
#    print(list(map(hex, i2c.scan())))
#    time.sleep(1)

# i2c.writeto( 0x70,dcps3(FINE_CONTROL,COARSE_CONTROL) )
i2c.writeto( 0x70,get_dcps3packet(FINE_CONTROL,COARSE_CONTROL, STAGE4_TUNE&0b11, STAGE5_TUNE&0b11) )

i2c.unlock()
CLK_ENB.value = True






