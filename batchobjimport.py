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
    # obj_input_dir = 'C:/Users/meule001/Downloads/split/'
    # output_gdb_path = 'C:/Users/meule001/Downloads/'
    # output_gdb_name = 'batchimport.gdb'
    output_fc_name = 'import'
    outputfc = output_gdb_path + '/' + output_gdb_name + '.gdb/' + output_fc_name
    outputfc2d = output_gdb_path + '/' + output_gdb_name + '.gdb/' + 'footprint2d'
    outputcfjoined = output_gdb_path + '/' + output_gdb_name + '/' + 'joined'

    print(obj_input_dir)
    # set input dir and create list list with import files
    arcpy.env.workspace = obj_input_dir
    print('workspace=' + arcpy.env.workspace)
    objlist = arcpy.ListFiles('*.obj')
    objlistpath = []
    for o in objlist:
        objlistpath.append(obj_input_dir + '/' + o)
    print(objlistpath[1])
    count_files = len(objlistpath)
    print(str(count_files) + ' obj files to import')

    # coordinate system RD New and NAP elevation for 3D BAG
    sr = arcpy.SpatialReference(28992, 5709)

    # create output database
    arcpy.env.overwriteOutput = True
    arcpy.management.CreateFileGDB(output_gdb_path, output_gdb_name)

    arcpy.env.workspace = output_gdb_path + '/' + output_gdb_name + '.gdb/'
    print('workspace2=' + arcpy.env.workspace)

    # import all listed files
    print('start import')
    arcpy.ddd.Import3DFiles(objlistpath, outputfc, False, sr)
    count_imported = int(str(arcpy.GetCount_management(outputfc)))

    if count_imported == count_files:
        print('all ' + str(count_imported) + ' files imported into: ' + outputfc)

    if count_imported < count_files:
        count_missing = count_files - count_imported
        print(str(count_imported) + ' files imported into: ' + outputfc + '  ' + str(count_missing) + ' missing')

        # check which files are imported
        imported_rows = arcpy.SearchCursor(outputfc, fields="Name")
        imported_list = []

        for row in imported_rows:
            imported_list.append("{}".format(row.getValue("Name")))
        # make list of not imported files
        not_imported = list(set(objlist) - set(imported_list))
        not_imported_file = output_gdb_path + output_gdb_name + '_missing.txt'

        with open(not_imported_file, "w") as outfile:
            outfile.write("\n".join(not_imported))

        print('check ' + not_imported_file + ' for missing files')

    if count_imported > count_files:
        print('import error: more files imported than input')

    # calculate 3d statistics
    print('calculate 3D statistics')
    arcpy.ddd.AddZInformation(outputfc, 'SURFACE_AREA; VOLUME')

    # create 2d footprint for ground area
    print('calculate 2d footprints and add footprint area to to attributes')
    arcpy.ddd.MultiPatchFootprint(outputfc, outputfc2d)

    arcpy.management.JoinField(outputfc, "Name", outputfc2d, "Name", "Shape_Area")


if __name__ == '__main__':
    obj_input_dir = sys.argv[1]
    output_gdb_path = sys.argv[2]
    output_gdb_name = sys.argv[3]
    main(obj_input_dir, output_gdb_path, output_gdb_name)
