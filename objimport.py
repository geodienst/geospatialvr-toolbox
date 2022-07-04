# C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3>python.exe C:\Users\meule001\Downloads\objsplit.py C:\Users\meule001\Downloads\objs\3dbag_v210908_fd2cee53_lod22_3d_7689.obj C:\Users\meule001\Downloads\split\

"""
Import a directory of obj files into a new file geodatabase feature class.

Run:

python batchobjimport.py INPUT_DIR OUTPUT_DIR OUTPUT_NAME
python batchobjimport.py  C:/Users/meule001/Downloads/split/ C:/Users/meule001/Downloads/ importgdb

"""

# import arcpy and 3d module
import sys
import arcpy
from arcpy import ddd



def main(obj_input_dir, output_gdb_path, output_gdb_name):
    output_fc_name = 'import'

    fullpathgdb = output_gdb_path + '/' + output_gdb_name + '.gdb'
    outputfc = fullpathgdb + "/" + output_fc_name
    outputfc2d = fullpathgdb + "/" + 'footprint2d'

    arcpy.AddMessage("importing files from {0}".format(obj_input_dir))

    # set input dir and create list list with import files
    arcpy.env.workspace = obj_input_dir

    objlist = arcpy.ListFiles('*.obj')

    # create output database
    arcpy.env.overwriteOutput = True
    arcpy.management.CreateFileGDB(output_gdb_path, output_gdb_name)

    arcpy.env.workspace = fullpathgdb
   
    # import all listed files
    import_obj_files(obj_input_dir, objlist, outputfc, output_gdb_path)

    # calculate 3d statistics
    arcpy.AddMessage('calculate 3D statistics')
    arcpy.ddd.AddZInformation(outputfc, 'SURFACE_AREA; VOLUME')


def import_obj_files(obj_input_dir, objlist, outputfc, output_gdb_path):
    objlistpath = []
    for o in objlist:
        objlistpath.append(obj_input_dir + '/' + o)
    # coordinate system RD New and NAP elevation for 3D BAG
    sr = arcpy.SpatialReference(28992, 5709)
    count_files = len(objlistpath)
    if count_files <= 1:
        arcpy.AddMessage('There is only 1 obj file, this is probably an error')
        sys.exit(-1)
    arcpy.AddMessage('start import')
    arcpy.AddMessage("{0} obj files to import".format(str(count_files)))

    arcpy.ddd.Import3DFiles(objlistpath, outputfc, False, sr)
    count_imported = int(str(arcpy.GetCount_management(outputfc)))
    arcpy.AddMessage("{0} obj files imported".format(str(count_imported)))
    if count_imported == count_files:
        arcpy.AddMessage('all ' + str(count_imported) + ' files imported into: ' + outputfc)

    if count_imported < count_files:
        count_missing = count_files - count_imported
        arcpy.AddMessage(str(count_imported) + ' files imported into: ' + outputfc + '  ' + str(count_missing) + ' missing')

        # check which files are imported
        imported_rows = arcpy.SearchCursor(outputfc, fields="Name")
        imported_list = []

        for row in imported_rows:
            imported_list.append("{}".format(row.getValue("Name")))
        # make list of not imported files
        not_imported = list(set(objlist) - set(imported_list))
        not_imported_file = output_gdb_path + 'missing.txt'

        with open(not_imported_file, "w") as outfile:
            outfile.write("\n".join(not_imported))

        arcpy.AddMessage('check ' + not_imported_file + ' for missing files')

    if count_imported > count_files:
        arcpy.AddMessage('import error: more files imported than input')


if __name__ == '__main__':
    obj_input_dir = sys.argv[1]
    output_gdb_path = sys.argv[2]
    output_gdb_name = sys.argv[3]
    main(obj_input_dir, output_gdb_path, output_gdb_name)
