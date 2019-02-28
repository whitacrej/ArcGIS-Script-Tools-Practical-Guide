#--------------------------------------------------------------------------------------------------------------------
# Name:        TableToCSV.py
# Purpose:     This script converts standalone tables to CSV tables.
#
# Author:      James V. Whitacre
#
# Created:     06/29/2016
# Modified:    06/09/2017
# Copyright:   (c) University of Illinois 2017
## Licence:     Forethcoming...
#--------------------------------------------------------------------------------------------------------------------

# Imports
import arcpy
import csv

# Parameters

# Input Table (Table View)
# ArcToolbox script tool validation: If table is from a geodatabase, enable alias_incl
table = arcpy.GetParameterAsText(0)

# Output Fields (Field: MultiValue = Yes; Filter = field [NOT Blob, Raster, XML])
if arcpy.GetParameterAsText(1).find(';') > -1:
    field_names = arcpy.GetParameterAsText(1).split(';')
else:
    field_names = [arcpy.GetParameterAsText(1)]

# Output CSV Table (File: Direction = Output; Filter = File [csv, txt])
out_file = arcpy.GetParameterAsText(2)

# Add Field Aliases to CSV Table (String: Type = Optional; Default = NONE; Filter = Value List [NONE, AS_HEADER, AS_ROW])
# ArcToolbox script tool validation:
#   If table is from a geodatabase, enable alias_incl
#   If geometry field is selected, enable geom_properties
alias_incl = arcpy.GetParameterAsText(3)

## Add subtype or domain values...???

# ArcToolbox script tool validation for the following Geometry Attributes parameters:
#   Enable parameter if input table is feature class
#   Categorize each parameter as 'Add Geometry Attributes' group

# Add Geometry Properties (String: Type = Optional; MultiValue = Yes; Filter = Value List [LENGTH, AREA, POINT_X_Y_Z_M,
#   EXTENT, LINE_START_MID_END, CENTROID, CENTROID_INSIDE, PART_COUNT, POINT_COUNT, LINE_BEARING, PERIMETER_LENGTH,
#   LENGTH_GEODESIC, LENGTH_3D, AREA_GEODESIC, PERIMETER_LENGTH_GEODESIC])
# ArcToolbox script tool validation:
#   Add Values to list based on geometry type
if arcpy.GetParameterAsText(4).find(';') > -1:
    geom_properties = arcpy.GetParameterAsText(4).upper().split(';')
else:
    geom_properties = [arcpy.GetParameterAsText(4).upper()]

# Length Unit (String: Type = Optional; Filter = Value List [FEET_US, METERS, KILOMETERS, MILES_US, NAUTICAL_MILES, YARDS])
l_unit = arcpy.GetParameterAsText(5)

# Area Unit (String: Type = Optional; Filter = Value List [ACRES, HECTARES, SQUARE_MILES_US, SQUARE_KILOMETERS, SQUARE_METERS, SQUARE_FEET_US, SQUARE_YARDS, SQUARE_NAUTICAL_MILES])
a_unit = arcpy.GetParameterAsText(6)

# Coordinate System (Spatial Reference: Type = Optional)
cs = arcpy.GetParameterAsText(7)
if not cs:
    cs = arcpy.env.outputCoordinateSystem


# Script

# Create a describe object of the input table
desc = arcpy.Describe(table)
table_field_list = [field.name for field in arcpy.ListFields(table)]

# If the table is a feature class and geometry properties are included, add geometry attributes
if desc.datasetType == u'FeatureClass' and geom_properties:
    arcpy.CopyFeatures_management(table, 'copy_table')
    table = 'copy_table'
    arcpy.AddGeometryAttributes_management(table, geom_properties, l_unit, a_unit, cs)
    geom_fields = [field.name for field in arcpy.ListFields(table) if field.name not in table_field_list]
    field_names = field_names + geom_fields

# If aliases are included: Create a list of all of the field aliases in the table
if alias_incl != 'NONE':
    # Create a list of all of the fields in the table
    aliases = [field.aliasName for field in arcpy.ListFields(table) if field.name in field_names]

with open(out_file,'wb') as f:
    # Create a CSV DictWriter for greater control of the data
    dw = csv.writer(f)

    # Write header to the output file
    if alias_incl == 'AS_HEADER':
        arcpy.AddMessage('Writing aliases as the header...')
        dw.writerow(aliases)
    else:
        dw.writerow(field_names)

    # If aliases are included as a row, create a dictionary of field names and field aliases and write to the output CSV file
    if alias_incl == 'AS_ROW':
        arcpy.AddMessage('Writing aliases as a row...')
        dw.writerow(aliases)

    # Use a search cursor to iterate through each row of the table to create a dictionary of field names and the row data for each field
    with arcpy.da.SearchCursor(table, field_names) as cursor:
        for row in cursor:
            dw.writerow(row)

# If the table is a feature class and geometry properties are included, delete the copy table
if desc.datasetType == u'FeatureClass' and geom_properties:
    arcpy.Delete_management(table)