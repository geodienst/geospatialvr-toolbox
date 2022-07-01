import sys
import arcpy
from arcpy import ddd


def main(imported_buildings):
    arcpy.AddMessage(imported_buildings)
    arcpy.AddMessage(arcpy.Describe(arcpy.Describe(imported_buildings).catalogPath).path)
    outputfc = imported_buildings
    outputfc2d = arcpy.Describe(arcpy.Describe(imported_buildings).catalogPath).path + "/" + 'foottprint2d'

    # create 2d footprint for ground area
    arcpy.AddMessage('calculate 2d footprints and add footprint area to to attributes')
    arcpy.ddd.MultiPatchFootprint(outputfc, outputfc2d)

    arcpy.management.JoinField(outputfc, "Name", outputfc2d, "Name", "Shape_Area")

    arcpy.AddMessage("{0} created".format(outputfc2d))


if __name__ == '__main__':
    imported_buildings = sys.argv[1]
    main(imported_buildings)

