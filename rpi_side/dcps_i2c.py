# Written for DCPS HOST2 Board
import time
import digitalio
import board
import busio


#Do not adjust by hand, use run_dcps_control script
FINE_CONTROL=66
COARSE_CONTROL=0
STAGE4_TUNE=3
STAGE5_TUNE=3
CHANNEL=3

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
        if i < fstep:
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
    i2c.writeto(0x71, bytes([ch_map[ch]]) )
    # result = bytearray(1)
    # i2c.readfrom_into(0x71, result)
    # print(result)
    i2c.unlock()

print("Board Name: ",board.board_id)

# PIXEL = LED = neopixel.NeoPixel(board.NEOPIXEL, 1) # RGB LED on board
CLK_ENB = digitalio.DigitalInOut(board.D11)
CLK_ALT = digitalio.DigitalInOut(board.D10)
RSTB = digitalio.DigitalInOut(board.D12)

CLK_ENB.direction = digitalio.Direction.OUTPUT
CLK_ALT.direction = digitalio.Direction.OUTPUT
RSTB.direction = digitalio.Direction.OUTPUT


CLK_ENB.value = False
# PIXEL.brightness = 0.3
# PIXEL.fill((0, 255, 255))

for i in range(1):
    RSTB.value = False
    time.sleep(1)
    RSTB.value = True
    time.sleep(1)

i2c = busio.I2C(board.SCL, board.SDA)
select_mux_channel(CHANNEL)
i2c.deinit()

i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
i2c.try_lock()
print("FINE_CONTROL:",FINE_CONTROL)
print("COARSE_CONTROL:",COARSE_CONTROL)
print(f"STAGE4_TUNE: {STAGE4_TUNE&0b11:02b}")
print(f"STAGE5_TUNE: {STAGE5_TUNE&0b11:02b}")
print("CHANNEL:", CHANNEL)

i2c.writeto(0x70, get_dcps3packet(FINE_CONTROL, COARSE_CONTROL, STAGE4_TUNE&0b11, STAGE5_TUNE&0b11))

i2c.unlock()
CLK_ENB.value = True