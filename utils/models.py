import arcpy
import os
from typing import Any, Generator, Hashable

from archelp import message

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
        self.__dict__.update(self.__class__(self.path).__dict__)
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
    ALL_FIELDS = object()
    """ Wrapper for basic Table operations """
    def __init__(self, path: os.PathLike):
        super().__init__(path)
        
        self._query: str = None
        self.fields: dict[str, arcpy.Field] = {field.name: field for field in arcpy.ListFields(self.path)}
        self.fieldnames: list[str] = list(self.fields.keys())
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
        if not self.validate_oid_field(): 
            self.OIDField = self.describe.OIDFieldName
            raise ValueError(f"{self.OIDField} must be unique")
        return
    
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
        """ Set the OID field for the table
        oid_field: field to use as OID
        
        **WARNING**: This can have unintended consequences if the OID field is not unique
        or if the OID field provided becomes non-unique after setting.
        Use validate_oid_field to check for uniqueness after making edits that could affect the OID field
        """
        if oid_field not in self.fieldnames: 
            raise ValueError(f"{oid_field} not in {self.fieldnames}")
        
        unique_count = len(set(self[oid_field]))
        if not len(self) == unique_count:
            raise ValueError(f"{oid_field} must be unique ({len(self) - unique_count} collisions)")
        
        self.OIDField = oid_field
    
    def validate_oid_field(self) -> bool:
        """ Validate the OID field for uniqueness """
        return len(self) == len(set(self[self.OIDField]))
    
    def get_rows(self, fields: list[str] = ALL_FIELDS, as_dict: bool = False, **kwargs) -> Generator[list | dict, None, None]:
        """ Get rows from a table 
        fields: list of fields to return
        as_dict: return rows as dict if True
        kwargs: See arcpy.da.SearchCursor for kwargs
        """
        if fields is Table.ALL_FIELDS or fields == ["*"]:
            fields = self.fieldnames
            
        if not self._validate_fields(fields):
            raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        
        kwargs["where_clause"] = self._handle_queries(kwargs)
        
        with arcpy.da.SearchCursor(self.path, fields, **kwargs) as cursor:
            for row in cursor:
                if as_dict: yield dict(zip(fields, row))
                if len(fields) == 1: yield row[0]
                yield row
                    
    def update_rows(self, key: str, update_dictionary: dict[Hashable, dict[str, Any]], **kwargs) -> int:
        """ Update rows in table
        key: field to use as key for update (must be in fields)
        update_dictionary: dict of key value pairs to update [fieldname/token: {field: value}]
        kwargs: See arcpy.da.UpdateCursor for allowed arguments
              : where_clause: SQL query to filter rows* This will be added to any active query
        return: number of rows updated
        """
        if not update_dictionary: raise ValueError("Values must be provided")
        
        fields = set([key])
        for val in update_dictionary.values(): fields.update(val.keys())
        
        if not self._validate_fields(list(fields)): raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
                
        kwargs["where_clause"] = self._handle_queries(kwargs)
        
        update_count = 0
        with self.update_cursor(fields, **kwargs) as cursor:
            # NOTE: Because we used set operations to get the fields, the order of the fields may not be the same as the table.
            #     : This is why we need to get the field order from the cursor object then map the update values back to the row
            
            for row in cursor:
                row_key = row_dict[key]  # Get the key value from the row
                if not row_key in update_dictionary.keys(): continue
                
                row_dict = dict(zip(fields, row))
                for field, value in update_dictionary[row_key].items(): 
                    row_dict[field] = value
                
                cursor.updateRow(list(row_dict.values()))  # Write the updated row back to the table
                update_count += 1
                
        self._updated = True
        return update_count

    def _handle_queries(self, kwargs):
        query = self._query
        if 'where_clause' in kwargs:
            query = kwargs['where_clause']
            del kwargs['where_clause']
        return query
    
    def _validate_fields(self, fields: list[str]) -> bool:
        """ Validate field list for cursors """
        if fields != ["*"] and not all([field in self.fieldnames + self.cursor_tokens for field in fields]):
            return False
        return True
    
    def _cursor(self, cur_type: str, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.UpdateCursor | arcpy.da.SearchCursor | arcpy.da.InsertCursor:
        """ Internal cursor method to get cursor type
        """
        if fields is Table.ALL_FIELDS or fields == ["*"]: fields = self.fieldnames
        if not self._validate_fields(fields): raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        
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
        kwargs['where_clause'] = self._handle_queries(kwargs)
        return self._cursor("update", fields, **kwargs)
    
    def search_cursor(self, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.SearchCursor:
        """ Get a search cursor for the table
        fields: list of fields to return
        kwargs: See arcpy.da.SearchCursor for kwargs
        return: search cursor
        """
        kwargs['where_clause'] = self._handle_queries(kwargs)
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
        if not values: raise ValueError("Values must be provided")
        
        fields = list(values[0].keys())
        if not self._validate_fields(fields): raise ValueError(f"Fields must be in {self.fieldnames + self.cursor_tokens}")
        
        insert_count = 0
        with self.insert_cursor(fields, **kwargs) as cursor:
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
        with self.update_cursor([key], **kwargs) as cursor:
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
    
    def delete_field(self, field_name: str) -> None:
        """ Delete a field from the table 
        field_name: name of the field to delete
        """
        arcpy.management.DeleteField(self.path, field_name)
        self.update()
        return
    
    def __iter__(self):
        yield from self.get_rows(self.fieldnames, as_dict=True)
        
    def __len__(self):
        if self.queried: return self._queried_count
        if not self._updated: return self.record_count
        
        self._updated = False
        return int(arcpy.management.GetCount(self.path).getOutput(0))
    
    def __getitem__(self, idx: int | str | list):
        
        if isinstance(idx, int):
            if idx not in self._oid_set: raise KeyError(f"{idx} not in {self.name}.{self.OIDField}{f' with query: {self.query}' if self.query else ''}")
            return next(self.get_rows(as_dict=True, where_clause=f"{self.OIDField} = {idx}"))
        
        if isinstance(idx, str):
            if idx in self.fieldnames + self.cursor_tokens:
                return [v for v in self.get_rows([idx])]
            elif idx in self._oid_set:
                return next(self.get_rows(as_dict=True, where_clause=f"{self.OIDField} = {idx}"))
            
            raise KeyError(f"{idx} not in {self.fieldnames + self.cursor_tokens}")
        
        if isinstance(idx, list) and all([isinstance(f, str) for f in idx]):
            if all([field in self.fieldnames + self.cursor_tokens for field in idx]):
                return [value for value in self.get_rows(idx, as_dict=True)]
            raise KeyError(f"{idx} not in {self.fieldnames + self.cursor_tokens}")
            
        if isinstance(idx, list) and all([isinstance(f, int) for f in idx]):
            return [value for value in self.get_rows(where_clause=f"{self.OIDField} IN {tuple(idx)}", as_dict=True)]
        raise ValueError(f"{idx} is invalid, either pass field, OID, or list of fields or list of OIDs")
    
    def __setitem__(self, idx: int | str | list, values: list | Any):
        
        if isinstance(idx, int) and len(values) == len(self.fieldnames):
            self.update_rows(self.OIDField, {idx: dict(zip(self.fieldnames, values))})
            return
        
        if isinstance(idx, str) and idx in self.fieldnames + self.cursor_tokens:
            with self.update_cursor([idx], where_clause=self.query) as cursor:
                for _ in cursor: cursor.updateRow([values])
            return
        
        if isinstance(idx, list) and all(field in self.fieldnames + self.cursor_tokens for field in idx):
            with self.update_cursor(idx, where_clause=self.query) as cursor:
                for _ in cursor: cursor.updateRow(values)
            return
        
        raise ValueError(f"{idx} not in {self.fieldnames + self.cursor_tokens} or index is out of range")
    
    def __delitem__(self, idx: int | str | list[str]):
        if isinstance(idx, int): 
            self.delete_rows(self.OIDField, [idx])
            return
        
        if isinstance(idx, str) and idx in self.fieldnames:
            self.delete_field(idx)
            self.update()
            return
        
        if isinstance(idx, list) and all(isinstance(field, str) for field in idx):
            if not all([field in self.fieldnames for field in idx]): 
                raise ValueError(f"{idx} not subset of {self.fieldnames}")
            
            for field in idx: self.delete_field(field)
            self.update()
            return
         
        if isinstance(idx, list) and all(isinstance(field, int) for field in idx):
            self.delete_rows(self.OIDField, idx)
            return
        
        raise KeyError(f"{idx} not in {self.fieldnames + self.cursor_tokens}")
    
    def update(self):
        """ Update the Table object and preserve custom attributes """
        new = self.__class__(self.path)
        
        # Preserve a custom OIDField
        if self.OIDField != new.OIDField and self.validate_oid_field(): new.OIDField = self.OIDField    
        # Preserve a custom query
        if self.query != new.query: new.query = self.query
        
        self.__dict__.update(new.__dict__)
        return
    
class FeatureClass(Table):
    """ Wrapper for basic FeatureClass operations """    
    def __init__(self, path: os.PathLike):
        super().__init__(path)
        self.spatialReference: arcpy.SpatialReference = self.describe.spatialReference
        self.shapeType: str = self.describe.shapeType
        self.cursor_tokens.extend(
            [
                "SHAPE@",
                "SHAPE@XY",
                "SHAPE@TRUECENTROID",
                "SHAPE@X",
                "SHAPE@Y",
                "SHAPE@Z",
                "SHAPE@M",
                "SHAPE@JSON",
                "SHAPE@WKB",
                "SHAPE@WKT",
                "SHAPE@AREA",
                "SHAPE@LENGTH",
            ]
        )
        self.fieldnames[self.fieldnames.index(self.describe.shapeFieldName)] = "SHAPE@"
      
class ShapeFile(FeatureClass): ...

class Dataset(DescribeModel): ...

class GeoDatabase(DescribeModel): ...