"""
Global Module
	Need 9 lines in input file
"""
GlobalEpsilon= int(input())
NumberFirstPL= int(input())
NumBlock= int(input())
PipelineList= []
NumAtkPL= int(input())
verbose= False

mice_ratio = int(input())
mice_scale= int(input())
elephant_ratio = int(input())
elephant_scale = int(input())

times = int(input())

def PrintConfig():
	print('GlobalEpsilon:', GlobalEpsilon)
	print('NumberFirstPL:', NumberFirstPL)
	print('NumBlock:', NumBlock)
	print('NumAtkPL:', NumAtkPL)
	print(f'mice: {mice_ratio}%,{mice_scale}')
	print(f'elephant: {elephant_ratio}%,{elephant_scale}')
