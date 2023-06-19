import sys
import time

import arcpy


def main(buildings, areas_of_interest, csv_file, shp_file):
    arcpy.AddMessage(buildings)
    gdbpath = arcpy.Describe(arcpy.Describe(buildings).catalogPath).path
    arcpy.AddMessage(gdbpath)

    index = gdbpath.rfind('\\')
    outputdirectory = gdbpath[0:index]
    arcpy.AddMessage('Output directory=' + outputdirectory)
    gsitable = gdbpath + '/groundspaceindex3' + str(time.time()).split('.')[0]
    arcpy.AddMessage('gsitable=' + gsitable)
    arcpy.gapro.SummarizeWithin(buildings, gsitable, "POLYGON", '', None, areas_of_interest, "ADD_SUMMARY", "SQUARE_METERS", "Shape_Area SUM", None, None, "NO_MIN_MAJ", None, None)

    arcpy.management.CalculateField(in_table=gsitable, field="gsi", expression="$feature.SUM_Area_SQUAREMETERS / $feature.Shape_Area",
                                    expression_type="ARCADE", code_block="", field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]


    arcpy.AddMessage('Create csv file with buildings')
    #csv file with buildings in polygons
    spatialjoin = gdbpath + '/SpatialJoin'
    arcpy.analysis.SpatialJoin(areas_of_interest, buildings, spatialjoin, "JOIN_ONE_TO_MANY", "KEEP_ALL", 'Name "File Name" true true false 255 Text 0 0,First,#,buildings,Name,0,255', "INTERSECT", None, '')
    arcpy.conversion.TableToTable(spatialjoin, outputdirectory, csv_file, '', 'Join_Count "Join_Count" true true false 4 Long 0 0,First,#,SpatialJoin,Join_Count,-1,-1;TARGET_FID "TARGET_FID" true true false 4 Long 0 0,First,#,SpatialJoin,TARGET_FID,-1,-1;JOIN_FID "JOIN_FID" true true false 4 Long 0 0,First,#,SpatialJoin,JOIN_FID,-1,-1;Name "File Name" true true false 255 Text 0 0,First,#,SpatialJoin,Name,0,255;SArea "SArea" true true false 8 Double 0 0,First,#,SpatialJoin,SArea,-1,-1;Volume "Volume" true true false 8 Double 0 0,First,#,SpatialJoin,Volume,-1,-1;Z_Min "Z_Min" true true false 8 Double 0 0,First,#,SpatialJoin,Z_Min,-1,-1;Z_Max "Z_Max" true true false 8 Double 0 0,First,#,Polygons_SpatialJoin4,Z_Max,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,SpatialJoin,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,SpatialJoin,Shape_Area,-1,-1', '')

    arcpy.AddMessage('Create shape file with areas of interest')
    #shp file with polygons
    #extra veld voor polygonid in shp file (OBJECTID komt niet in shp file)

    arcpy.management.AddField(gsitable, "polygonid", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.CalculateField(gsitable, "polygonid", "!OBJECTID!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")



    #arcpy.conversion.FeatureClassToFeatureClass(areas_of_interest, outputdirectory, shp_file, '', r'Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,' + areas_of_interest +
    #                                            ',Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,' + areas_of_interest +
    #                                            ',Shape_Area,-1,-1;polygonid "polygonid" true true false 4 Long 0 0,First,#,' + areas_of_interest + ',polygonid,-1,-1', '')
    arcpy.conversion.FeatureClassToFeatureClass(gsitable, outputdirectory, shp_file)


if __name__ == '__main__':
    areas_of_interest = sys.argv[1]
    buildings = sys.argv[2]
    shp_file = sys.argv[3]
    csv_file = sys.argv[4]
    main(buildings, areas_of_interest, csv_file, shp_file)
