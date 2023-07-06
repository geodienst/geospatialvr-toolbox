import sys
import arcpy
from arcpy import ddd
import objimport
from math import floor


def main(obj_input_dir, output_gdb_path, output_gdb_name, floor_height):
    arcpy.AddMessage("Floor height {0}".format(floor_height))
    output_fc_name = 'import'

    fullpathgdb = output_gdb_path + '/' + output_gdb_name + '.gdb'
    outputfc = fullpathgdb + "/" + output_fc_name
    outputfc2d = fullpathgdb + "/" + 'buildings'

    # Set the progressor
    arcpy.SetProgressor("step", "Importing objfiles en calculate some statistics", 0, 4, 1)

    arcpy.AddMessage("importing files from {0}".format(obj_input_dir))

    # set input dir and create list list with import files
    arcpy.env.workspace = obj_input_dir
    objlist = arcpy.ListFiles('*.obj')

    # create output database
    arcpy.env.overwriteOutput = True
    arcpy.management.CreateFileGDB(output_gdb_path, output_gdb_name)

    arcpy.env.workspace = fullpathgdb

    # import all listed files
    showProgress("Importing files from:{0}".format(obj_input_dir), 1)
    objimport.import_obj_files(obj_input_dir, objlist, outputfc, output_gdb_path)

    # calculate 3d statistics
    showProgress("Calculate 3D statistics", 2)
    arcpy.ddd.AddZInformation(outputfc, 'SURFACE_AREA; VOLUME')

    # create 2d footprint for ground area
    showProgress('Calculate 2d footprints and add footprint area to the attributes', 3)
    arcpy.ddd.MultiPatchFootprint(outputfc, outputfc2d)

    arcpy.management.JoinField(outputfc, "Name", outputfc2d, "Name", "Shape_Area")

    arcpy.AddMessage("{0} created".format(fullpathgdb))

    arcpy.AddMessage("Calculate Floor area")
    # arcpy.management.CalculateField(in_table=outputfc2d, field="Floor_Area", expression="round(($feature.Z_Max - $feature.Z_Min)/2.5) * $feature.Shape_Area, 3)",
    #                                 expression_type="ARCADE")

    arcpy.management.CalculateField(outputfc2d, "Floor_Area", "math.floor((!Z_Max! - !Z_Min!)/{})*!Shape_Area!".format(floor_height), "PYTHON3", '', "DOUBLE", "NO_ENFORCE_DOMAINS")

    #s hapefile
    arcpy.AddMessage('Create shapefile with buildings: ' + 'buildings.shp')
    arcpy.conversion.FeatureClassToFeatureClass(outputfc2d, output_gdb_path, 'buildings.shp')

    arcpy.AddMessage("Buildings feature class {0} created".format(outputfc2d))

    spatialReference = arcpy.Describe(outputfc2d).spatialReference
    arcpy.AddMessage("Spatial Reference {0}".format(spatialReference.Name))

    # add feature class for area of interest
    arcpy.management.CreateFeatureclass(fullpathgdb, "areasofinterest", "POLYGON", None, "DISABLED", "DISABLED", spatialReference, '', 0, 0, 0, '')

    # add buildings fc and areasofinterest fc to map
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    arcpy.AddMessage('NR maps {0}'.format(len(aprx.listMaps("Map"))))
    if len(aprx.listMaps("Map")) == 1:
        aprxMap = aprx.listMaps("Map")[0]
        aprxMap.addDataFromPath(outputfc2d)
        aprxMap.addDataFromPath(fullpathgdb + "/" + "areasofinterest")


def showProgress(text, step):
    arcpy.SetProgressorLabel(text)
    arcpy.SetProgressorPosition(step)
    arcpy.AddMessage(text)


if __name__ == '__main__':
    obj_input_dir = sys.argv[1]
    output_gdb_path = sys.argv[2]
    output_gdb_name = sys.argv[3]
    floor_height = float(sys.argv[4])
    main(obj_input_dir, output_gdb_path, output_gdb_name, floor_height)
