import arcpy
class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    self.params[3].enabled = False
    self.params[4].enabled = False
    self.params[5].enabled = False
    self.params[6].enabled = False
    self.params[7].enabled = False

    self.params[4].category = 'Add Geometry Attributes'
    self.params[5].category = 'Add Geometry Attributes'
    self.params[6].category = 'Add Geometry Attributes'
    self.params[7].category = 'Add Geometry Attributes'

    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parameter
    has been changed."""
    if self.params[0].value and not self.params[0].hasBeenValidated:
        try:

            desc = arcpy.Describe(self.params[0].value)

            # If 'Input Table' is populated with a FileGDB table, enable parameter: 'Add Field Aliaases to CSV Table (optional)'
            if '.gdb' in desc.path:
                self.params[3].enabled = True
            else:
                self.params[3].enabled = False

            # If 'Input Table' is populated with a FileGDB table, enable parameter: 'Add Field Aliaases to CSV Table (optional)'
            if desc.datasetType == u'FeatureClass':
                self.params[4].enabled = True
                self.params[5].enabled = True
                self.params[6].enabled = True
                self.params[7].enabled = True

                shapeType = desc.shapeType
                sr = desc.spatialReference
                gcsOrMercator = False if not sr.GCSName and sr.PCSName.upper().find("MERCATOR") == -1 else True

                if shapeType.upper() == "POINT":
                    self.params[4].filter.list = ["POINT_X_Y_Z_M"]
                elif shapeType.upper() == "MULTIPOINT":
                    self.params[4].filter.list = ["CENTROID", "PART_COUNT", "EXTENT"]
                elif shapeType.upper() == "POLYLINE":
                    if desc.hasZ:
                        lineList = ["LENGTH", "LENGTH_GEODESIC", "LENGTH_3D", "LINE_START_MID_END", "CENTROID", "CENTROID_INSIDE", "PART_COUNT", "POINT_COUNT", "LINE_BEARING", "EXTENT"]
                    else:
                        lineList = ["LENGTH", "LENGTH_GEODESIC", "LINE_START_MID_END", "CENTROID", "CENTROID_INSIDE", "PART_COUNT", "POINT_COUNT", "LINE_BEARING", "EXTENT"]
                    self.params[4].filter.list = lineList
                    if gcsOrMercator:
                        lineList.remove("LENGTH")
                        if desc.hasZ:
                            lineList.remove("LENGTH_3D")
                        self.params[4].filter.list = lineList
                elif shapeType.upper() == "POLYGON":
                    polyList = ["AREA", "AREA_GEODESIC", "PERIMETER_LENGTH", "PERIMETER_LENGTH_GEODESIC", "CENTROID", "CENTROID_INSIDE", "LINE_START_MID_END", "PART_COUNT", "POINT_COUNT", "EXTENT"]
                    self.params[4].filter.list = polyList
                    if gcsOrMercator:
                        polyList.remove("AREA")
                        polyList.remove("PERIMETER_LENGTH")
                        self.params[4].filter.list = polyList

            else:
                self.params[4].enabled = False
                self.params[5].enabled = False
                self.params[6].enabled = False
                self.params[7].enabled = False



        except:
            pass
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    return
