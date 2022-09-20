import arcpy


def main(output_gdb_path, output_gdb_name, area_of_interest, buildings):
    # Script execution code goes here
    fullpathgdb = output_gdb_path + '/' + output_gdb_name + '.gdb'
    summarized = fullpathgdb + "/gsivalues"
    Output_Grouped_Table = ""
    Building_Area_Field = "Shape_Area"
    arcpy.analysis.SummarizeWithin(in_polygons=area_of_interest, in_sum_features=buildings, out_feature_class=summarized, keep_all_polygons="KEEP_ALL",
                                   sum_fields=[[Building_Area_Field, "Sum"]], sum_shape="ADD_SHAPE_SUM", shape_unit="SQUAREMETERS",
                                   group_field="", add_min_maj="NO_MIN_MAJ", add_group_percent="NO_PERCENT", out_group_table=Output_Grouped_Table)

    ground_space_index = arcpy.management.CalculateField(in_table=summarized, field="gsi", expression="$feature.SUM_Area_SQUAREMETERS / $feature.Shape_Area",
                                                         expression_type="ARCADE", code_block="", field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]

    return


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':
    # Tool parameter accessed with GetParameter or GetParameterAsText
    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)
    param2 = arcpy.GetParameterAsText(2)
    param3 = arcpy.GetParameterAsText(3)
    main(param0, param1, param2, param3)
    
    # Update derived parameter values using arcpy.SetParameter() or arcpy.SetParameterAsText()
