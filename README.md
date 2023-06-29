# Geospatial VR Toolbox #

This toolbox allows for exchanging data between ArcGIS (Pro) and the Merkator City software.

The toolbox contains of several tools:

* objsplit.py: split up .OBJ files with multiple objects into single files (based on gist [balazsdukai/objsplit.py](https://gist.github.com/balazsdukai/dca936c72bd7a596fea5e4a2bb34a912) )
* import_and_footprint.py: Import a directory of obj files into a new file geodatabase feature class.
* calculate_fsi.py: calculate the floor space index 
* calculate_gsi.py: calculate the ground space index


### Using inside ARCGIS Pro ###

* Download the zipfile from the download directory
* Unzip the files
* Add the toolbox to a project
* Start with 01 Split obj, make use of the i icon and the help icon
* In step 3 you have to draw an area of interest, which you can use in step 4a en 4b


### Requirements ###

* Arcpy environment based on ArcGIS Pro version 3.1

The tool is developed based on data from [© 3D BAG by tudelft3d](https://3dbag.nl/en/download) 
