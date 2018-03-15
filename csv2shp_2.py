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
		outShapefile = 'C:/Users/USER/Desktop/output.shp'
		# Remove output shapefile if it already exists
		if os.path.exists(outShapefile):
			driver.DeleteDataSource(outShapefile)
		dstfile = driver.CreateDataSource(outShapefile) # Your output file
		dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=ogr.wkbLineString) 

		# Add the other attribute fields needed with the following schema :
		fielddef = ogr.FieldDefn("MMSI", ogr.OFTString)
		fielddef.SetWidth(10)
		dstlayer.CreateField(fielddef)
		
		fielddef = ogr.FieldDefn("S_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
	
		fielddef = ogr.FieldDefn("E_time", ogr.OFTString)
		fielddef.SetWidth(80)
		dstlayer.CreateField(fielddef)
	
		#-----------------
		df = pd.read_csv('C:/Users/USER/Desktop/AISDATA/kaohsiung.csv', sep=',', error_bad_lines=False, index_col=False, dtype='unicode')
		MMSI = df['MMSI'].tolist()
		Lon = df['Longitude'].tolist()
		Lat= df['Latitude'].tolist()
		Time = df['Record_Time'].tolist()
		front_time = None
		for mmsi,time in zip(MMSI,Time):
			if not(MMSI is None):
				
				if (MMSI[0]!=mmsi):
					#count the number of the repeat MMSI[0]
					count = MMSI.count(MMSI[0])
					#make line
					if (count>1):
						line = ogr.Geometry(ogr.wkbLineString)
						for Long,Lati in zip(Lon[:count],Lat[:count]):
							line.AddPoint(float(Long), float(Lati))
						feature = ogr.Feature(dstlayer.GetLayerDefn())
						feature.SetGeometry(line)
						feature.SetField("MMSI", MMSI[0])
						feature.SetField("S_time", Time[0])
						feature.SetField("E_time", Time[count-1])
						dstlayer.CreateFeature(feature)
						print('%s point count = %s') %(MMSI[0],count)
					#remove the used feature
					Lon = Lon[count:]
					Lat = Lat[count:]
					Time = Time[count:]
					MMSI = MMSI[count:]
					
				elif (front_time is not None):
					#print('%s-') %(Time.index(time))
					t2 = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
					t1 = datetime.datetime.strptime(front_time,'%Y-%m-%d %H:%M:%S')
					#18000sec = 5hr
					if((t2-t1).seconds>18000):
						index = Time.index(time)
						#print(time)
						#print('index = %s') %(index)
						if(index>1):
							line = ogr.Geometry(ogr.wkbLineString)
							for Long,Lati in zip(Lon[:index],Lat[:index]):
								line.AddPoint(float(Long), float(Lati))
							feature = ogr.Feature(dstlayer.GetLayerDefn())
							feature.SetGeometry(line)
							feature.SetField("MMSI", MMSI[0])
							feature.SetField("S_time", Time[0])
							feature.SetField("E_time", Time[index-1])
							dstlayer.CreateFeature(feature)
							print('%s point count = %s') %(MMSI[0],index)
						Lon = Lon[index:]
						Lat = Lat[index:]
						Time = Time[index:]
						MMSI = MMSI[index:]
					
				front_time = time
			else:
				print('left MMSI = %s') %(MMSI)
		
		
test = qgismakeline()
test.select()
print('----------finished---------')

#np.savetmmsit('C:/Users/USER/Desktop/test.tmmsit', df.values, delimiter=",", fmt="%s")
#np.savetmmsit('C:/Users/USER/Desktop/test.tmmsit', string, delimiter=",", fmt="%s")