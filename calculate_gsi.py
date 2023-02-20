import os

import arcpy
import time

def main(shape_file, buildings):
    # Script execution code goes here
    #fullpathgdb = output_gdb_path + '/' + output_gdb_name + '.gdb'
    arcpy.env.overwriteOutput = True
    gdbpath = arcpy.Describe(arcpy.Describe(buildings).catalogPath).path
    arcpy.AddMessage("gdbpath=" + gdbpath)
    arcpy.env.workspace = gdbpath
    arcpy.AddMessage("Adding projection to shape file")
    arcpy.management.DefineProjection(shape_file, 'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]')

    # add shapefile to gdbpath
    head, tail = os.path.split(shape_file)
    areas_of_interest = gdbpath + '/' + tail.split('.')[0]
    arcpy.conversion.FeatureClassToGeodatabase(shape_file, gdbpath)

    gsitable = gdbpath + "/groundspaceindex3" + str(time.time()).split('.')[0]
    Output_Grouped_Table = ""
    Building_Area_Field = "Shape_Area"
    arcpy.gapro.SummarizeWithin(buildings, gsitable, "POLYGON", '', None, areas_of_interest, "ADD_SUMMARY", "SQUARE_METERS", "Shape_Area SUM Count", None, None, "NO_MIN_MAJ", None, None)

    arcpy.management.CalculateField(in_table=gsitable, field="gsi", expression="round(($feature.SUM_Area_SQUAREMETERS / $feature.Shape_Area), 3)",
                                expression_type="ARCADE", code_block="", field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # export
    # shapefile
    gsi_file = 'gsioutput.shp'
    arcpy.AddMessage("outputdirectory: " + head)
    arcpy.AddMessage("File with gsi: " + gsi_file)
    arcpy.conversion.FeatureClassToFeatureClass(gsitable, head, gsi_file)


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':
    # Tool parameter accessed with GetParameter or GetParameterAsText
    area_of_interest = arcpy.GetParameterAsText(0)
    buildings = arcpy.GetParameterAsText(1)
    # buildings = gdb_path + "\\footprint2d"
    arcpy.AddMessage('Areas of Interest: ' + area_of_interest)
    arcpy.AddMessage('Buildings: ' + buildings)
    main(area_of_interest, buildings)
    
    # Update derived parameter values using arcpy.SetParameter() or arcpy.SetParameterAsText()
