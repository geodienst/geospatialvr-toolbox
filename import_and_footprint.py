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

    #shapefile
    arcpy.AddMessage('Create shapefile with buildings: ' + 'buildings.shp')
    arcpy.conversion.FeatureClassToFeatureClass(outputfc2d, output_gdb_path, 'buildings.shp')

    arcpy.AddMessage("Buildings feature class {0} created".format(outputfc2d))

    # add feature class for area of interest
    arcpy.management.CreateFeatureclass(fullpathgdb, "areaofinterest", "POLYGON", None, "DISABLED", "DISABLED",
                                        'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]];-30515500 -30279500 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision', '', 0, 0, 0, '')

    # add buildings fc and areasofinterest fc to map
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprxMap = aprx.listMaps("Map")[0]
    aprxMap.addDataFromPath(outputfc2d)
    aprxMap.addDataFromPath(fullpathgdb + "/" + "areaofinterest")

def showProgress(text, step):
    arcpy.SetProgressorLabel(text)
    arcpy.SetProgressorPosition(step)
    arcpy.AddMessage(text)


# def import_obj_files(obj_input_dir, objlist, outputfc, output_gdb_path):
#     objlistpath = []
#     for o in objlist:
#         objlistpath.append(obj_input_dir + '/' + o)
#     # coordinate system RD New and NAP elevation for 3D BAG
#     sr = arcpy.SpatialReference(28992, 5709)
#     count_files = len(objlistpath)
#     if count_files <= 1:
#         arcpy.AddMessage('There is only 1 obj file, this is probably an error')
#         sys.exit(-1)
#     arcpy.AddMessage('start import')
#     arcpy.AddMessage("{0} obj files to import".format(str(count_files)))
#
#     arcpy.ddd.Import3DFiles(objlistpath, outputfc, False, sr)
#     count_imported = int(str(arcpy.GetCount_management(outputfc)))
#     arcpy.AddMessage("{0} obj files imported".format(str(count_imported)))
#     if count_imported == count_files:
#         arcpy.AddMessage('all ' + str(count_imported) + ' files imported into: ' + outputfc)
#
#     if count_imported < count_files:
#         count_missing = count_files - count_imported
#         arcpy.AddMessage(str(count_imported) + ' files imported into: ' + outputfc + '  ' + str(count_missing) + ' missing')
#
#         # check which files are imported
#         imported_rows = arcpy.SearchCursor(outputfc, fields="Name")
#         imported_list = []
#
#         for row in imported_rows:
#             imported_list.append("{}".format(row.getValue("Name")))
#         # make list of not imported files
#         not_imported = list(set(objlist) - set(imported_list))
#         not_imported_file = output_gdb_path + '\missing.txt'
#
#         with open(not_imported_file, "w") as outfile:
#             outfile.write("\n".join(not_imported))
#
#         arcpy.AddMessage('check ' + not_imported_file + ' for missing files')
#
#     if count_imported > count_files:
#         arcpy.AddMessage('import error: more files imported than input')


if __name__ == '__main__':
    obj_input_dir = sys.argv[1]
    output_gdb_path = sys.argv[2]
    output_gdb_name = sys.argv[3]
    floor_height = int(sys.argv[4])
    main(obj_input_dir, output_gdb_path, output_gdb_name, floor_height)
