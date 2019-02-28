# -*- coding: UTF-8 -*-
''' Metadata, Copyright, License:
----------------------------------------------------------------------------------------------------
Name:       TableToCSV.py
Purpose:    This script converts tables to CSV tables with field selection.
Author:     Whitacre, James V.
Created:    2019/02/28
Copyright:  Copyright 2019
Licence:    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this 
            file except in compliance with the License. You may obtain a copy of the License at 
            http://www.apache.org/licenses/LICENSE-2.0
            Unless required by applicable law or agreed to in writing, software distributed under 
            the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
            KIND, either express or implied. See the License for the specific language governing 
            permissions and limitations under the License.​
----------------------------------------------------------------------------------------------------
'''

''' Import Modules '''
import arcpy
import csv

''' Parameters '''

table = arcpy.GetParameterAsText(0) # Input Table (Table View; Validation: If table is from a geodatabase, enable alias_incl)

field_names = arcpy.GetParameterAsText(1).split(';') if ';' in arcpy.GetParameterAsText(1) else arcpy.GetParameterAsText(1) # Output Fields (Field; MultiValue: Yes; Filter: field [NOT Blob, Raster, XML]; Validation: If geometry field is selected, enable geom_properties)

out_file = arcpy.GetParameterAsText(2) # Output CSV Table (File; Direction: Output; Filter: File [csv, txt])

alias_incl = arcpy.GetParameterAsText(3) # Add Field Aliases to CSV Table (String; Type: Optional; Default: NONE; Filter:  Value List [NONE, AS_HEADER, AS_ROW])

geom_properties = arcpy.GetParameterAsText(4).split(';') if ';' in arcpy.GetParameterAsText(4) else arcpy.GetParameterAsText(4) # Add Geometry Properties (String; Type:  Optional; MultiValue:  Yes; Filter:  Value List [LENGTH, AREA, POINT_X_Y_Z_M, EXTENT, LINE_START_MID_END, CENTROID, CENTROID_INSIDE, PART_COUNT, POINT_COUNT, LINE_BEARING, PERIMETER_LENGTH, LENGTH_GEODESIC, LENGTH_3D, AREA_GEODESIC, PERIMETER_LENGTH_GEODESIC]; Validation: Enable parameter if input table is feature class, Add Values to list based on geometry type)

l_unit = arcpy.GetParameterAsText(5) # Length Unit (String; Type: Optional; Filter:  Value List [FEET_US, METERS, KILOMETERS, MILES_US, NAUTICAL_MILES, YARDS])

a_unit = arcpy.GetParameterAsText(6) # Area Unit (String; Type:  Optional; Filter:  Value List [ACRES, HECTARES, SQUARE_MILES_US, SQUARE_KILOMETERS, SQUARE_METERS, SQUARE_FEET_US, SQUARE_YARDS, SQUARE_NAUTICAL_MILES])

cs = arcpy.GetParameterAsText(7) # Coordinate System (Spatial Reference; Type: Optional)


''' Script '''

# Create a describe object of the input table
desc = arcpy.Describe(table)
# List all fields
table_field_list = [field.name for field in desc.fields]

# If the table is a feature class and geometry properties are included, add geometry attributes
if desc.datasetType == 'FeatureClass' and geom_properties:
    arcpy.SetProgressorLabel('Adding Geometry Attributes...')
    # If a coordinate system is not given, use the feature class coordinate system
    if not cs:
        cs = desc.spatialReference
    arcpy.CopyFeatures_management(table, 'copy_table')
    table = 'copy_table'
    arcpy.AddGeometryAttributes_management(table, geom_properties, l_unit, a_unit, cs)
    geom_fields = [field.name for field in desc.fields if field.name not in table_field_list]
    field_names = field_names + geom_fields

# If aliases are included: Create a list of all of the field aliases in the table
if alias_incl != 'NONE':
    # Create a list of all of the fields in the table
    aliases = [field.aliasName for field in desc.fields if field.name in field_names]

# Create and open output CSV file
with open(out_file, 'w', newline='') as f:
    # Create a CSV Writer
    dw = csv.writer(f)

    # Write aliases or fields names as the header to the output CSV file
    if alias_incl == 'AS_HEADER':
        dw.writerow(aliases)
        arcpy.AddMessage('Aliases written as the header...')
    else:
        dw.writerow(field_names)

    # Write aliases as a row to output CSV file if 'AS_ROW' is selected
    if alias_incl == 'AS_ROW' and aliases:
        dw.writerow(aliases)
        arcpy.AddMessage('Aliases written as a row...')

    # Set the progressor, first count the number of records
    rows = int(arcpy.GetCount_management(table)[0])
    arcpy.SetProgressor('step', 'Writing {0} rows to CSV file...'.format(rows), 0, rows, 1)
    
    # Use a search cursor to iterate through each row of the table and write to the output CSV file
    with arcpy.da.SearchCursor(table, field_names) as cursor:
        for row in cursor:
            dw.writerow(row)

            # Update the progressor position
            arcpy.SetProgressorPosition()

# If the table is a feature class and geometry properties are included, delete the copy table
if desc.datasetType == 'FeatureClass' and geom_properties:
    arcpy.Delete_management(table)

# Add a 'script completed' message
arcpy.AddMessage('CSV file complete: {0} rows and {1} fields copied.'.format(rows, len(field_names)))