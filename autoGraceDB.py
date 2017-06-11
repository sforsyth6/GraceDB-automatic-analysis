import pandas as pd
import numpy as np
from splinter import Browser
import time
from astropy.time import Time


#Converting the text file into a pandas dataframe for easy use
text = open('MergedCandidates_for_Notices.2016-10-16_13_51.txt', 'r')

tempCandid = {}

#Convert the text file into a easily usable dataFrame
for line in text:
	temp = line.split()
	if len(temp) == 0:
		pass
	elif temp[0] == 'File':
		category = temp
		for num in range(len(category)):
			tempCandid[category[num]] = []
		tempCandid['GRBType'] = []
	elif temp[0] == '!':
		for num in range(len(category)+1):
			if num < 4:
				tempCandid[category[num]].append(temp[num+1])
			elif num == 4:
				tempCandid['GRBType'].append(temp[num+1])
			elif num > 4:
				tempCandid[category[num-1]].append(temp[num+1])

candidates = pd.DataFrame(tempCandid)

#Remove any grbs that are not long
for index in candidates.GRBType.index:
	grb = candidates.GRBType.loc[candidates.index==index]
	grbType =  grb.iloc[0].replace('.','')
	if grbType != 'PL':
		candidates = candidates.drop(index,axis=0)

#Remove any GRBs with a azimuthel angle near the horizon (there's an issue with the code in this region for now. Remove this when it's fixed)
for index in candidates.Az.index:
	az = float(candidates.Az.loc[candidates.index==index].iloc[0])
	if az >= 0 and az <= 8:
		candidates = candidates.drop(index,axis=0)
	elif az >= 172 and az <= 188:
		candidates = candidates.drop(index,axis=0)
	elif az >= 352 and az <=360:
		candidates = candidates.drop(index,axis=0)


#Convert from MET to GPS
candidates = candidates.reset_index(drop=True)
gps = []
for index in candidates.index:
	date = candidates.date.loc[candidates.index==index].iloc[0]
	utc = candidates.UTC.loc[candidates.index==index].iloc[0]
	iso = date + ' '+  utc
	t = Time(iso)
	t.format = 'gps'
	gps.append(str(t.value))

candidates['GPS'] = pd.Series(gps)

#Set up line for xpipeline
line = []
for index in candidates.index:
	date = candidates.date.loc[candidates.index==index].iloc[0].split('-')
	year = date[0][2:]
	xpipe = ['SL000000' + str(index+1),'Fermi','GRBc' + str(year)+str(date[1])+str(date[2]),'Long',candidates.UTC.loc[candidates.index==index].iloc[0],candidates.GPS.loc[candidates.index==index].iloc[0],'','', 
		candidates.RA.loc[candidates.index==index].iloc[0] , candidates.Dec.loc[candidates.index==index].iloc[0], candidates.Err.loc[candidates.index==index].iloc[0], 'Nan', 'No']
	line.append( ' '.join(xpipe))

print line


