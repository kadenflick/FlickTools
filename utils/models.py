import arcpy
import os
from typing import Any, Generator

# Get class names implemented in current module

class DescribeModel:
    """ Base object for models """
    
    DATATYPE: str = "Describe Model"
    
    def __init__(self, featurepath: os.PathLike):
        self.featurepath = featurepath
        desc = self._validate()
        
        # Set General Properties
        self.describe: Any = desc
        self.basename: str = desc.baseName
        self.workspace: os.PathLike = desc.path
        self.name: str = desc.name
        self.catalogpath: os.PathLike = desc.catalogPath
        self.extension: str = desc.extension
        self.type: str = desc.dataType
        return
    
    def update(self):
        """ Update the Describe object """
        updates = self.__class__(self.featurepath)
        self.__dict__.update(updates.__dict__)
        return
    
    def _validate(self):
        """ Validate the featurepath and return the Describe object """
        if arcpy.Exists(self.featurepath):
            # Get Describe object
            desc = arcpy.Describe(self.featurepath)
            # Raise TypeError if the datatype is not the expected datatype
            if desc.dataType != self.DATATYPE and self.DATATYPE != "Describe Model":
                raise TypeError(f"{desc.baseName} is {desc.dataType}, must be {self.DATATYPE}")
            return desc
        
        raise FileNotFoundError(f"{self.featurepath} does not exist")
    
    def __repr__(self):
        return f"<{self.DATATYPE}: {self.basename} @ {hex(id(self))}>"
    
    def __str__(self):
        return f"{self.DATATYPE}: {self.basename}"


## TABLE LIKE OBJECTS

class Table(DescribeModel):
    """ Wrapper for basic Table operations """
    DATATYPE: str = "Table"

    def __init__(self, tablepath: os.PathLike):
        super().__init__(tablepath)
        self.fields: list[arcpy.Field] = self.describe.fields
        self.fieldnames: list[str] = [field.name for field in self.fields]
        self.indexes: list[arcpy.Index] = self.describe.indexes
        self.OIDField: str = self.describe.OIDFieldName
        self.cursor_tokens: list[str] = \
            [
                "CREATED@",
                "CREATOR@",
                "EDITED@",
                "EDITOR@",
                "GLOBALID@",
                "OID@",
                "SUBTYPE@",
            ]
        return
    
    def get_rows(self, fields: list[str], as_dict: bool = False, **kwargs) -> Generator[list | dict, None, None]:
        """ Get rows from table takes field list and kwags for search cursor"""
        if fields != ["*"] and not all([field in self.fieldnames + self.cursor_tokens for field in fields]):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        with arcpy.da.SearchCursor(self.featurepath, fields, **kwargs) as cursor:
            for row in cursor:
                if as_dict:
                    yield dict(zip(fields, row))
                else:
                    yield row
                    
    def update_rows(self, fields: list[str], key: str, values: dict[str: ...], **kwargs):
        """ Update rows in table
        fields: list of fields to update
        key: field to use as key for update (must be in fields)
        values: dict of key value pairs to update [field: value]
        """
        if not all([field in self.fieldnames + self.cursor_tokens for field in fields]):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        if key not in fields:
            raise ValueError(f"Key must be in {fields}")
        if not all([field in fields for field in values.keys()]):
            raise ValueError(f"Values must be in {fields}")
        with arcpy.da.UpdateCursor(self.featurepath, fields, **kwargs) as cursor:
            for row, value in zip(cursor, values):
                row = value
                cursor.updateRow(row)
        return
    
class FeatureClass(Table):
    """ Wrapper for basic FeatureClass operations """
    DATATYPE: str = "FeatureClass"
    
    def __init__(self, shppath: os.PathLike):
        super().__init__(shppath)
        self.spatialReference: arcpy.SpatialReference = self.describe.spatialReference
        self.shapeType: str = self.describe.shapeType
        self.cursor_tokens.extend(
            [
                "SHAPE@XY",
                "SHAPE@TRUECENTROID",
                "SHAPE@X",
                "SHAPE@Y",
                "SHAPE@Z",
                "SHAPE@M",
                "SHAPE@JSON",
                "SHAPE@WKB",
                "SHAPE@WKT",
                "SHAPE@",
                "SHAPE@AREA",
                "SHAPE@LENGTH",
            ]
        )
   
class ShapeFile(FeatureClass):
    """ Wraper for basic Shapefile operations"""
    DATATYPE: str = "ShapeFile"

## END TABLE LIKE OBJECTS

## GEODATABASE LIKE OBJECTS
class Dataset(DescribeModel):
    """ Wrapper for basic Dataset operations """
    DATATYPE: str = "Dataset"

class GeoDatabase(DescribeModel):
    """ Wrapper for basic GeoDatabase operations """
    DATATYPE: str = "GeoDatabase"


# TESTS

TEST_PATH = r"F:\GIS\Henderson\Shapefiles\Buildings\Buildings.shp"
shp = ShapeFile(TEST_PATH)
print(shp.DATATYPE, shp.name, shp)
repr(shp)

for row in shp.get_rows(["SHAPE@"], as_dict=False, where_clause=f"{shp.OIDField} < 10"):
    row.keys()