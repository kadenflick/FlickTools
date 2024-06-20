import arcpy
import os
from typing import Any, Generator

from archelp import message

# Sentinels
ALL_FIELDS = object()

class DescribeModel:
    """ Base object for models """
        
    def __init__(self, path: os.PathLike):
        self.path = path
        desc = self._validate()
                
        # Set General Properties
        self.describe: Any = desc
        self.basename: str = desc.baseName
        self.workspace: os.PathLike = desc.path
        self.name: str = desc.name
        self.catalogpath: os.PathLike = desc.catalogPath
        self.extension: str = desc.extension
        self.type: str = desc.dataType
        self.data: dict[int, dict[str, Any]] = None
        return
    
    def update(self):
        """ Update the Describe object """
        new = self.__class__(self.path)
        # Preserve a custom OIDField
        if hasattr(new, "OIDField") and self.OIDField != new.OIDField:
            new.OIDField = self.OIDField
        # Preserve a custom query
        if hasattr(new, "query") and self.query != new.query:
            new.query = self.query
        self.__dict__.update(new.__dict__)
        return
    
    def _validate(self):
        """ Validate the featurepath and return the Describe object """
        if arcpy.Exists(self.path):
            # Get Describe object
            desc = arcpy.Describe(self.path)
            # Raise TypeError if the datatype is not the expected datatype
            if desc.dataType != type(self).__name__ and type(self).__name__ != "Describe Model":
                raise TypeError(f"{desc.baseName} is {desc.dataType}, must be {type(self).__name__}")
            return desc
        
        raise FileNotFoundError(f"{self.path} does not exist")
    
    def __repr__(self):
        return f"<{type(self).__name__}: {self.basename} @ {hex(id(self))}>"
    
    def __str__(self):
        return f"{type(self).__name__}: {self.basename}"

class Table(DescribeModel):
    """ Wrapper for basic Table operations """
    def __init__(self, tablepath: os.PathLike):
        super().__init__(tablepath)
        
        self._query: str = None
        self.fields: dict[str, arcpy.Field] = {field.name: field for field in arcpy.ListFields(self.path)}
        self.fieldnames: list[str] = list(self.fields.keys())
        if hasattr(self.describe, "shapeFieldName"):
            shape_idx = self.fieldnames.index(self.describe.shapeFieldName)
            self.fieldnames[shape_idx] = "SHAPE@"   # Default to include full shape
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
                "*"
            ]
        self.queried: bool = False
        self._queried_count: int = 0
        self._oid_set = set(self[self.OIDField])
        self._updated: bool = False
        self.record_count: int = int(arcpy.management.GetCount(self.path).getOutput(0))
        return
    
    def _validate_fields(self, fields: list[str]) -> bool:
        """ Validate field list for cursors """
        if fields != ["*"] and not all([field in self.fieldnames + self.cursor_tokens for field in fields]):
            return False
        return True
    
    @property
    def row_template(self) -> dict[str, Any]:
        """ Get a template for a row """
        return dict(zip(self.fieldnames, [None for _ in range(len(self.fieldnames))]))
    
    @property
    def query(self) -> str:
        """ Get the query string """
        return self._query
    
    @query.setter
    def query(self, query_string: str):
        """ Set the query string """
        if not query_string:
            del self.query
        try:
            with arcpy.da.SearchCursor(self.path, [self.OIDField], where_clause=query_string) as cur:
                cur.fields
        except Exception as e:
            message(f"Invalid query string ({query_string})", "warning")
        self._query = query_string
        self.data = [row for row in self]
        self._queried_count = len(self.data)
        self.queried = True
        self._oid_set = set(self[self.OIDField])
        return
    
    @query.deleter
    def query(self):
        """ Delete the query string """
        self._query = None
        self.queried = False
        self.data = None
        self._oid_set = set(self[self.OIDField])
        return
    
    def set_oid_field(self, oid_field: str) -> None:
        if oid_field in self.fieldnames:
            found = set()
            for v in self[oid_field]:
                if v in found:
                    raise ValueError(f"{oid_field} must be unique")
                found.add(v)
            self.OIDField = oid_field
    
    def get_rows(self, fields: list[str] = ALL_FIELDS, as_dict: bool = False, **kwargs) -> Generator[list | dict, None, None]:
        """ Get rows from a table 
        fields: list of fields to return
        as_dict: return rows as dict if True
        kwargs: See arcpy.da.SearchCursor for kwargs
        """
        if fields == ALL_FIELDS or fields == ["*"]:
            fields = self.fieldnames
        if not self._validate_fields(fields):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        
        query = self._query
        if 'where_clause' in kwargs:
            query = kwargs['where_clause']
            del kwargs['where_clause']
        
        with arcpy.da.SearchCursor(self.path, fields, where_clause=query, **kwargs) as cursor:
            for row in cursor:
                if as_dict:
                    yield dict(zip(fields, row))
                else:
                    if len(fields) == 1: yield row[0]
                    else: yield row
                    
    def update_rows(self, key: str, values: dict[Any, dict[str, Any]], **kwargs) -> int:
        """ Update rows in table
        key: field to use as key for update (must be in fields)
        values: dict of key value pairs to update [fieldname/token: value]
        kwargs: See arcpy.da.UpdateCursor for kwargs
        return: number of rows updated
        """
        if not values:
            raise ValueError("Values must be provided")
        fields = list(list(values.values())[0].keys())
        if not self._validate_fields(fields):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        for val in values.values():
            if list(val.keys()) != fields:
                raise ValueError(f"Fields must match for all values in values dict")
        
        query = self._query
        if 'where_clause' in kwargs:
            query = kwargs['where_clause']
            del kwargs['where_clause']
        
        update_count = 0
        with arcpy.da.UpdateCursor(self.path, fields, where_clause=query, **kwargs) as cursor:
            for row in cursor:
                row_dict = dict(zip(fields, row))
                if row_dict[key] in values.keys():
                    cursor.updateRow(list(values[row_dict[key]].values()))
                    update_count += 1
        self._updated = True
        return update_count
    
    def _cursor(self, cur_type: str, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.UpdateCursor | arcpy.da.SearchCursor | arcpy.da.InsertCursor:
        """ Internal cursor method to get cursor type
        """
        if fields is ALL_FIELDS or fields == ["*"]:
            fields = self.fieldnames
        if not self._validate_fields(fields):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        if cur_type == "search":
            return arcpy.da.SearchCursor(self.path, fields, where_clause=self.query, **kwargs)
        if cur_type == "update":
            self._updated = True
            return arcpy.da.UpdateCursor(self.path, fields, where_clause=self.query, **kwargs)
        if cur_type == "insert":
            self._updated = True
            return arcpy.da.InsertCursor(self.path, fields, **kwargs)
        raise ValueError(f"Invalid cursor type {cur_type}")
    
    def update_cursor(self, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.UpdateCursor:
        """ Get an update cursor for the table
        fields: list of fields to update
        kwargs: See arcpy.da.UpdateCursor for kwargs
        return: update cursor
        """
        return self._cursor("update", fields, **kwargs)
    
    def search_cursor(self, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.SearchCursor:
        """ Get a search cursor for the table
        fields: list of fields to return
        kwargs: See arcpy.da.SearchCursor for kwargs
        return: search cursor
        """
        return self._cursor("search", fields, **kwargs)
    
    def insert_cursor(self, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.InsertCursor:
        """ Get an insert cursor for the table
        fields: list of fields to insert
        kwargs: See arcpy.da.InsertCursor for kwargs
        return: insert cursor
        """
        return self._cursor("insert", fields, **kwargs)
    
    def insert_rows(self, values: list[dict[Any, dict[str, Any]]], **kwargs) -> int:
        """ Insert rows into table
        fields: list of fields to insert
        values: list of dicts with key value pairs to insert [field: value]
        return: number of rows inserted
        """
        if not values:
            raise ValueError("Values must be provided")
        fields = list(values[0].keys())
        if not self._validate_fields(fields):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        
        insert_count = 0
        with arcpy.da.InsertCursor(self.path, fields, **kwargs) as cursor:
            for value in values:
                cursor.insertRow([value[field] for field in fields])
                insert_count += 1
        self._updated = True
        return insert_count
    
    def delete_rows(self, key: str, values: list[Any], **kwargs) -> int:
        """ Delete rows from table
        key: field to use as key for delete (must be in fields)
        values: list of values to delete
        kwargs: See arcpy.da.UpdateCursor for kwargs
        return: number of rows deleted
        """
        if not values:
            raise ValueError("Values must be provided")
        delete_count = 0
        with arcpy.da.UpdateCursor(self.path, [key], **kwargs) as cursor:
            for row in cursor:
                if row[0] in values:
                    cursor.deleteRow()
                    delete_count += 1
        self.update()
        return delete_count
    
    def add_field(self, field_name: str, **kwargs) -> None:
        """ Add a field to the table 
        field_name: name of the field to add
        kwargs: See arcpy.management.AddField for kwargs
        """
        arcpy.management.AddField(self.path, field_name, **kwargs)
        self.update()
        return
    
    def delete_fields(self, field_names: list[str]) -> None:
        """ Delete a field from the table 
        field_name: name of the field to delete
        """
        arcpy.management.DeleteField(self.path, field_names)
        self.update()
        return
    
    def __iter__(self):
        yield from self.get_rows(self.fieldnames, as_dict=True)
        
    def __len__(self):
        if self.queried:
            return self._queried_count
        if not self._updated:
            return self.record_count
        self._updated = False
        return int(arcpy.management.GetCount(self.path).getOutput(0))
    
    def __getitem__(self, idx: int | str | list):
        
        if isinstance(idx, int):
            if idx in self._oid_set:
                return self.get_rows(as_dict=True, where_clause=f"{self.OIDField} = {idx}").__next__()
            raise KeyError(f"{idx} not in {self.name}.{self.OIDField}{f' with query: {self.query}' if self.query else ''}")
        
        if isinstance(idx, str):
            if idx in self.fieldnames + self.cursor_tokens:
                return [v for v in self.get_rows([idx])]
            elif idx in self._oid_set:
                return self.get_rows(as_dict=True, where_clause=f"{self.OIDField} = {idx}").__next__()
            raise KeyError(f"{idx} not in {self.fieldnames + self.cursor_tokens}")
        
        if isinstance(idx, list) and all([isinstance(f, str) for f in idx]):
            if set(idx).issubset(self.fieldnames + self.cursor_tokens):
                return [v for v in self.get_rows(idx, as_dict=True)]
            raise KeyError(f"{idx} not in {self.fieldnames + self.cursor_tokens}")
            
        if isinstance(idx, list) and all([isinstance(f, int) for f in idx]):
            return [v for v in self.get_rows(where_clause=f"{self.OIDField} IN {tuple(idx)}", as_dict=True)]
        raise ValueError(f"{idx} is invalid, either pass field, OID, or list of fields or list of OIDs")
    
    def __setitem__(self, idx: int | str | list, values: list | Any):
        
        if isinstance(idx, int) and len(values) == len(self.fieldnames):
            self.update_rows(self.OIDField, {idx: dict(zip(self.fieldnames, values))})
            return
        
        if isinstance(idx, str) and idx in self.fieldnames + self.cursor_tokens:
            with arcpy.da.UpdateCursor(self.path, [idx], where_clause=self.query) as cursor:
                for row in cursor:
                    row[0] = values
                    cursor.updateRow(row)
            return
        
        if isinstance(idx, list) and set(idx).issubset(set(self.fieldnames + self.cursor_tokens)):
            with arcpy.da.UpdateCursor(self.path, idx, where_clause=self.query) as cursor:
                for row in cursor:
                    cursor.updateRow(values)
            return
        
        raise ValueError(f"{idx} not in {self.fieldnames + self.cursor_tokens} or index is out of range")
    
    def __delitem__(self, idx: int | str | list[str]):
        if isinstance(idx, int):
            self.delete_rows(self.OIDField, [idx])
            return
        
        if isinstance(idx, str) and idx in self.fieldnames:
            self.delete_fields([idx])
            self.update()
            return
        
        if isinstance(idx, list) and all(isinstance(field, str) for field in idx):
            if all([field in self.fieldnames for field in idx]):
                self.delete_fields(idx)
                return
            else:
                raise ValueError(f"{idx} not subset of {self.fieldnames}")
            
        if isinstance(idx, list) and all(isinstance(field, int) for field in idx):
            self.delete_rows(self.OIDField, idx)
            return
        raise KeyError(f"{idx} not in {self.fieldnames + self.cursor_tokens}")
    
class FeatureClass(Table):
    """ Wrapper for basic FeatureClass operations """    
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
      
class ShapeFile(FeatureClass): ...

class Dataset(DescribeModel): ...

class GeoDatabase(DescribeModel): ...