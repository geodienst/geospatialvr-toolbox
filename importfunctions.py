# import arcpy and 3d module
import arcpy
from arcpy import ddd


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
