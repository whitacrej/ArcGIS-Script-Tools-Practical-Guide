# -*- coding: UTF-8 -*-
''' Metadata, Copyright, License:
----------------------------------------------------------------------------------------------------
Name:       TableToCSV.py
Purpose:    This script converts tables to CSV tables with field selection.
Author:     Student, Python
Source:     https://github.com/whitacrej/ArcGIS-Script-Tools-Practical-Guide
            Created by James V. Whitacre
Created:    2019/03/04
Copyright:  Copyright 2019 James V. Whitacre
Licence:    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this 
            file except in compliance with the License. You may obtain a copy of the License at 
            http://www.apache.org/licenses/LICENSE-2.0
            Unless required by applicable law or agreed to in writing, software distributed under 
            the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
            KIND, either express or implied. See the License for the specific language governing 
            permissions and limitations under the License.
----------------------------------------------------------------------------------------------------
'''

''' Import Modules '''
import arcpy
import csv

''' Parameters '''

table = arcpy.GetParameterAsText(0) # Input Table (Param Type; Param Notes)

field_names = arcpy.GetParameterAsText(1) # Output Fields (Field; MultiValue: Yes; Filter: field [NOT Shape, Blob, Raster, XML])

out_file = arcpy.GetParameterAsText(2) # Output CSV Table (Param Type; Param Notes)

alias_incl = arcpy.GetParameterAsText(3) # Add Field Aliases to CSV Table (String; Type: Optional; Default: NONE; Filter:  Value List [NONE, AS_HEADER, AS_ROW])


''' Script '''

# Create a describe object of the input table
desc = arcpy.Describe(table)

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

# Add a 'script completed' message
arcpy.AddMessage('CSV file complete: {0} rows and {1} fields copied.'.format(rows, len(field_names)))