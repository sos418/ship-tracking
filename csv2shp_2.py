import ogr, osr, csv
import mysql.connector
import pandas as pd
import numpy as np
import os
import datetime, time

class qgismakeline:

	def select(self):
	
		spatialref = osr.SpatialReference()  # Set the spatial ref.
		spatialref.SetWellKnownGeogCS('WGS84')  # WGS84 aka ESPG:4326
		#create output Layer
		driver = ogr.GetDriverByName("ESRI Shapefile")
		outShapefile = 'C:/Users/USER/Desktop/output3.shp'
		# Remove output shapefile if it already exists
		if os.path.exists(outShapefile):
			driver.DeleteDataSource(outShapefile)
		dstfile = driver.CreateDataSource(outShapefile) # Your output file
		dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=ogr.wkbLineString) 

		# Add the other attribute fields needed with the following schema :
		fielddef = ogr.FieldDefn("MMSI", ogr.OFTString)
		fielddef.SetWidth(10)
		dstlayer.CreateField(fielddef)
		
		fielddef = ogr.FieldDefn("Start_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
	
		fielddef = ogr.FieldDefn("End_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
		
		fielddef = ogr.FieldDefn("Total_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
		
		#-----------------
		date_format_in = input('date format (1.%Y-%m-%d %H:%M:%S 2.%Y/%m/%d %H:%M:%S or 3.input format) :')
		if(date_format_in == 1):
			date_format = '%Y-%m-%d %H:%M:%S'
		elif(date_format_in == 2):
			date_format = '%Y/%m/%d %H:%M:%S'
		else:
			date_format = raw_input('input format: ')
		
		cutting_time = raw_input('cutting time(second): ')
		df = pd.read_csv('C:/Users/USER/Desktop/AISDATA/416004745.csv', sep=',', error_bad_lines=False, index_col=False, dtype='unicode')
		MMSI = df['MMSI'].tolist()
		Lon = df['Longitude'].tolist()
		Lat= df['Latitude'].tolist()
		Time = df['Record_Time'].tolist()
		front_time = None
		MMSILength = len(MMSI)-1
		print(df.index)
		i = 0
		
		for idx,(mmsi,time) in enumerate(zip(MMSI,Time)):
			if not(MMSI is None):
				if (MMSI[0]!=mmsi):
					i +=1
					count = MMSI.count(MMSI[0])
					#print('after this will change')
					#print('%s point count = %s') %(MMSI[0],count)
					print('%s get %s line')%(MMSI[0],i)
					print('')
					print('--> %s')%(mmsi)
					i=0
					#make line
					if (count>1):
						#total time counting
						Start_time_count = datetime.datetime.strptime(Time[0],date_format)
						End_time_count = datetime.datetime.strptime(Time[count-1],date_format)
						total_time_count = '%s hour %s second'\
						%(abs(int((End_time_count-Start_time_count).total_seconds())/3600),abs((End_time_count-Start_time_count).seconds)%3600)
						#
						line = ogr.Geometry(ogr.wkbLineString)
						for Long,Lati in zip(Lon[:count],Lat[:count]):
							line.AddPoint(float(Long), float(Lati))
						feature = ogr.Feature(dstlayer.GetLayerDefn())
						feature.SetGeometry(line)
						feature.SetField("MMSI", MMSI[0])
						feature.SetField("Start_time", Time[0])
						feature.SetField("End_time", Time[count-1])
						feature.SetField("Total_time", total_time_count)
						dstlayer.CreateFeature(feature)
						
					#remove the used feature
					Lon = Lon[count:]
					Lat = Lat[count:]
					Time = Time[count:]
					MMSI = MMSI[count:]
					
				elif (front_time is not None):
					t2 = datetime.datetime.strptime(time,date_format)
					t1 = datetime.datetime.strptime(front_time,date_format)
					t4 = abs((t2-t1).total_seconds())
					#input cutting time
					if(t4 > int(cutting_time) or idx == MMSILength):
						i +=1
						index_c = Time.index(time)
						#total time counting
						Start_time_count = datetime.datetime.strptime(Time[0],date_format)
						End_time_count = datetime.datetime.strptime(Time[index_c-1],date_format)
						total_time_count = '%s hour %s second'\
						%(abs(int((End_time_count-Start_time_count).total_seconds())/3600),abs((End_time_count-Start_time_count).seconds)%3600)
						#
						if(index_c>1):
							line = ogr.Geometry(ogr.wkbLineString)
							for Long,Lati in zip(Lon[:index_c],Lat[:index_c]):
								line.AddPoint(float(Long), float(Lati))
							feature = ogr.Feature(dstlayer.GetLayerDefn())
							feature.SetGeometry(line)
							feature.SetField("MMSI", MMSI[0])
							feature.SetField("Start_time", Time[0])
							if (idx == MMSILength):
								feature.SetField("End_time", Time[index_c])
								#print('end')
								#print('%s point count = %s') %(MMSI[0],index_c)
								print('%s get %s line')%(MMSI[0],i)
							else:
								feature.SetField("End_time", Time[index_c-1])
								#print('not end')
								#print('%s point count = %s') %(MMSI[0],index_c)
							feature.SetField("Total_time", total_time_count)
							dstlayer.CreateFeature(feature)
							
						Lon = Lon[index_c:]
						Lat = Lat[index_c:]
						Time = Time[index_c:]
						MMSI = MMSI[index_c:]
						
				front_time = time
test = qgismakeline()
test.select()
print('finished !')

#np.savetmmsit('C:/Users/USER/Desktop/test.tmmsit', df.values, delimiter=",", fmt="%s")
#np.savetmmsit('C:/Users/USER/Desktop/test.tmmsit', string, delimiter=",", fmt="%s")
