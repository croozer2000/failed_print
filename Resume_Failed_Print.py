from os import path
from math import floor

def Find_Layer(line,layer):
    index = line.find(f";LAYER:{layer}")
    return index

def Find_Homing_Line(line):
    index = line.find(f"G28")
    return index

def Find_G92_line(line):
    index = line.find(f"G92")
    return index

def Find_Move(line, axis):
    height = -1
    tmp = line.find(axis)
    if (line.find("G1") > -1 or line.find("G0") > -1) and tmp > -1:
        sl1 = line[tmp:].split(' ')
        sl1 = sl1[0]
        height = sl1.replace(axis,'').replace('\n','')
    return height

# user input variables
layer_height = .2
failed_height = 39.33
failed_layer = floor(failed_height/layer_height)
file_path = ".\gcodes\CE3E3V2_fronttire_v4 - CleanWheel_V1_ShallowTire.gcode"

# lines = fp.readlines()
count = 0
failed_layer_line = -1
home_line = -1
extruder_reset_G92_line = -1
z_height = -1
e_distance = -1

from random import randint
fixed_file_path = f'.\\gcodes\\fixed_{randint(0,100)}.gcode'
fp_fix = open(fixed_file_path,'x')

line_queue = []
def G92_line(extruder_distance):
    ts = extruder_distance.replace('\n','')
    return f"G92 E{ts} ;extruder resest\n"

def Move(height, axis, speed=300):
    return f"G0 {axis}{height} F{speed}\n"

def Fixed_Gcode(line,line_count):
    writeLine = True
    newLine = line
    global line_queue
    global z_height
    if home_line != -1 and (line_count > home_line and failed_layer_line == -1):
        writeLine = False
    if line_count == extruder_reset_G92_line:
        writeLine = False
    if line_count >= failed_layer_line and failed_layer_line != -1:
        if e_distance == -1:
            writeLine = False
            line_queue.append(line)
        else:
            if len(line_queue) > 0:
                fp_fix.write(G92_line(e_distance))
                fp_fix.write(Move(z_height,"Z"))
                fp_fix.writelines(line_queue)
                line_queue = []
    if writeLine:
        fp_fix.write(newLine)

    
with open(file_path, 'r') as fp:
    for line_number, line in enumerate(fp):
        secnd_process = True
        if Find_Layer(line,failed_layer) > -1:
            failed_layer_line = line_number
            print(f"Found line at {failed_layer_line}")
        elif failed_layer_line > -1 and e_distance == -1:
                e_distance = Find_Move(line,"E")
        else:
            if home_line == -1 and Find_Homing_Line(line) > -1:
                home_line = line_number
                print(home_line)
            if extruder_reset_G92_line == -1 and Find_G92_line(line) > -1:
                extruder_reset_G92_line = line_number
                print(extruder_reset_G92_line)
            tmp_z = Find_Move(line,"Z")
            z_height = tmp_z if tmp_z != -1 else z_height
        Fixed_Gcode(line,line_number)
        count += 1

