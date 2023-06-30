#
Compress-Archive -Path index.tbx,objimport.py,objsplit.py,calculate_fsi.py,calculate_gsi.py,import_and_footprint.py -DestinationPath download/geospatialvr-toolbox.zip -Force

Write-Output 'Zip file created for distribution'