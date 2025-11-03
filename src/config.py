"""
Global Module
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
	print('mice_ratio:', mice_ratio)
	print('mice_scale:', mice_scale)
	print('elephant_ratio:', elephant_ratio)
	print('elephant_scale:', elephant_scale)
