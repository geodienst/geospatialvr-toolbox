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
    spatialReference = arcpy.Describe(buildings).spatialReference
    arcpy.AddMessage("spatialReference=" + spatialReference.Name)
    arcpy.management.DefineProjection(shape_file, spatialReference)

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
