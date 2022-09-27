import os
import re
import sys
from contextlib import contextmanager
import os.path as p
import arcpy


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def main(shape_file, obj_file, output_dir):

    #split_obj
    if not os.path.exists(output_dir + '/objfiles'):
        arcpy.AddMessage('Creating directory for objfiles')
        os.mkdir(output_dir + '/objfiles')
    obj_input_dir = output_dir + '/objfiles'
    obj_split(obj_file, obj_input_dir)

    gdb = output_dir + '/geospatialvr.gdb'
    areas = gdb + '/' + shape_file.split('.')[0]
    outputfc = gdb + '/outputfc'
    outputfc2d = gdb + '/outputfc2d'



    # set input dir and create list list with import files
    arcpy.env.workspace = obj_input_dir
    objlist = arcpy.ListFiles('*.obj')

    # create output database
    arcpy.env.overwriteOutput = True
    arcpy.management.CreateFileGDB(output_dir, 'geospatialvr.gdb')
    arcpy.AddMessage("{0} created".format(gdb))
    arcpy.env.workspace = output_dir
    arcpy.conversion.FeatureClassToGeodatabase(shape_file, gdb)
    arcpy.AddMessage('Importing shapefile ' + shape_file + ' into ' + gdb)

    importobjfiles(obj_input_dir, objlist, outputfc, gdb)

    # calculate 3d statistics
    arcpy.AddMessage("Calculate 3D statistics")
    arcpy.ddd.AddZInformation(outputfc, 'SURFACE_AREA; VOLUME')

    # create 2d footprint for ground area
    arcpy.AddMessage('Calculate 2d footprints and add footprint area to the attributes')
    arcpy.ddd.MultiPatchFootprint(outputfc, outputfc2d)

    arcpy.management.JoinField(outputfc, "Name", outputfc2d, "Name", "Shape_Area")

    gsitable = gdb + '/groundspaceindex3' + str(time.time()).split('.')[0]
    arcpy.AddMessage('gsitable=' + gsitable)
    arcpy.gapro.SummarizeWithin(outputfc2d, gsitable, "POLYGON", '', None, areas, "ADD_SUMMARY", "SQUARE_METERS", "Shape_Area SUM", None, None, "NO_MIN_MAJ", None, None)
    arcpy.management.CalculateField(in_table=gsitable, field="gsi", expression="round(($feature.SUM_Area_SQUAREMETERS / $feature.Shape_Area), 3)",
                                    expression_type="ARCADE", code_block="", field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # export to csv
    arcpy.AddMessage('Create csv file with buildings and areas: ' + 'output.csv')
    # csv file with buildings in polygons
    spatialjoin = gdb + '/SpatialJoin'
    arcpy.analysis.SpatialJoin(areas, outputfc2d, spatialjoin, "JOIN_ONE_TO_MANY", "KEEP_ALL", 'Name "File Name" true true false 255 Text 0 0,First,#,buildings,Name,0,255', "INTERSECT", None, '')
    arcpy.conversion.TableToTable(spatialjoin, output_dir, 'output.csv', '', 'Join_Count "Join_Count" true true false 4 Long 0 0,First,#,SpatialJoin,Join_Count,-1,-1;TARGET_FID "TARGET_FID" true true false 4 Long 0 0,First,#,SpatialJoin,TARGET_FID,-1,-1;JOIN_FID "JOIN_FID" true true false 4 Long 0 0,First,#,SpatialJoin,JOIN_FID,-1,-1;Name "File Name" true true false 255 Text 0 0,First,#,SpatialJoin,Name,0,255;SArea "SArea" true true false 8 Double 0 0,First,#,SpatialJoin,SArea,-1,-1;Volume "Volume" true true false 8 Double 0 0,First,#,SpatialJoin,Volume,-1,-1;Z_Min "Z_Min" true true false 8 Double 0 0,First,#,SpatialJoin,Z_Min,-1,-1;Z_Max "Z_Max" true true false 8 Double 0 0,First,#,Polygons_SpatialJoin4,Z_Max,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,SpatialJoin,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,SpatialJoin,Shape_Area,-1,-1', '')

    arcpy.AddMessage('Create shapefile with global space index: ' + 'output.shp')
    #shapefile
    arcpy.conversion.FeatureClassToFeatureClass(gsitable, output_dir, 'output.shp')

def obj_split(file_in, dir_out):
    v_pat = re.compile(r"^v\s[\s\S]*")  # vertex
    vn_pat = re.compile(r"^vn\s[\s\S]*")  # vertex normal
    f_pat = re.compile(r"^f\s[\s\S]*")  # face
    o_pat = re.compile(r"^o\s[\s\S]*")  # named object
    ml_pat = re.compile(r"^mtllib[\s\S]*")  # .mtl file
    mu_pat = re.compile(r"^usemtl[\s\S]*")  # material to use
    s_pat = re.compile(r"^s\s[\s\S]*")  # shading
    vertices = ['None']  # because OBJ has 1-based indexing
    v_normals = ['None']  # because OBJ has 1-based indexing
    objects = {}
    faces = []
    mtllib = None
    usemtl = None
    shade = None
    o_id = None

    with open(file_in, 'r') as f_in:
        for line in f_in:
            v = v_pat.match(line)
            o = o_pat.match(line)
            f = f_pat.match(line)
            vn = vn_pat.match(line)
            ml = ml_pat.match(line)
            mu = mu_pat.match(line)
            s = s_pat.match(line)

            if v:
                vertices.append(v.group())
            elif vn:
                v_normals.append(vn.group())
            elif o:
                if o_id:
                    objects[o_id] = {'faces': faces,
                                     'usemtl': usemtl,
                                     's': shade}
                    o_id = o.group()
                    faces = []
                else:
                    o_id = o.group()
            elif f:
                faces.append(f.group())
            elif mu:
                usemtl = mu.group()
            elif s:
                shade = s.group()
            elif ml:
                mtllib = ml.group()
            else:
                # ignore vertex texture coordinates, polygon groups, parameter
                # space vertices
                pass

        if o_id:
            objects[o_id] = {'faces': faces,
                             'usemtl': usemtl,
                             's': shade}
        else:
            sys.exit("Cannot split an OBJ without named objects in it!")

    # vertex indices of a face
    fv_pat = re.compile(r"(?<= )\b[0-9]+\b", re.MULTILINE)
    # vertex normal indices of a face
    fn_pat = re.compile(r"(?<=\/)\b[0-9]+\b(?=\s)", re.MULTILINE)
    for o_id in objects.keys():
        faces = ''.join(objects[o_id]['faces'])
        f_vertices = {int(v) for v in fv_pat.findall(faces)}
        f_vnormals = {int(vn) for vn in fn_pat.findall(faces)}
        # vertex mapping to a sequence starting with 1
        v_map = {str(v): str(e) for e, v in enumerate(f_vertices, start=1)}
        vn_map = {str(vn): str(e) for e, vn in enumerate(f_vnormals, start=1)}
        faces_mapped = re.sub(fv_pat, lambda x: v_map[x.group()], faces)
        faces_mapped = re.sub(
            fn_pat, lambda x: vn_map[x.group()], faces_mapped)

        objects[o_id]['vertices'] = f_vertices
        objects[o_id]['vnormals'] = f_vnormals
        # old vertex indices are not needed anymore
        objects[o_id]['faces'] = faces_mapped

    oid_pat = re.compile(r"(?<=o\s).+")
    with suppress_stdout():
        for o_id in objects.keys():
            fname = oid_pat.search(o_id).group()
            file_out = p.join(dir_out, fname + ".obj")
            with open(file_out, 'w', newline=None) as f_out:
                if mtllib:
                    f_out.write(mtllib)

                f_out.write(o_id)

                for vertex in objects[o_id]['vertices']:
                    print(vertex)
                    f_out.write(vertices[int(vertex)])

                for normal in objects[o_id]['vnormals']:
                    f_out.write(v_normals[int(normal)])

                if objects[o_id]['usemtl']:
                    f_out.write(objects[o_id]['usemtl'])

                if objects[o_id]['s']:
                    f_out.write(objects[o_id]['s'])

                f_out.write(objects[o_id]['faces'])


def importobjfiles(obj_input_dir, objlist, outputfc, output_gdb_path):
    objlistpath = []
    for o in objlist:
        objlistpath.append(obj_input_dir + '/' + o)
    # coordinate system RD New and NAP elevation for 3D BAG
    sr = arcpy.SpatialReference(28992, 5709)
    count_files = len(objlistpath)
    if count_files <= 1:
        arcpy.AddMessage('There is only 1 obj file, this is probably an error')
        sys.exit(-1)
    arcpy.AddMessage('start importing obj files')
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
    shape_file = sys.argv[1]
    obj_file = sys.argv[2]
    output_dir = sys.argv[3]
    arcpy.AddMessage('---------------------------------------------------------------------')
    arcpy.AddMessage('Shapefile with areas of interest: ' + shape_file)
    arcpy.AddMessage('obj file with 3D data: ' + obj_file)
    arcpy.AddMessage('output directory: ' + output_dir)
    arcpy.AddMessage('---------------------------------------------------------------------')
    main(shape_file, obj_file, output_dir)