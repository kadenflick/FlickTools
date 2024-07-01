import arcpy
import os

from typing import overload, Any, Generator, Iterable, MutableMapping, Mapping

from archelp import message

class DescribeModel:
    """ Base object for models """
        
    def __init__(self, path: os.PathLike):
        self.path = path
        desc = self._validate()    
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
        return f"<{str(self)} @ {hex(id(self))}>"
    
    def __str__(self):
        return f"{type(self).__name__}: {self.basename} - {self.path}"

class Table(DescribeModel, MutableMapping):
    """ Wrapper for basic Table operations """
    
    ALL_FIELDS = object()
    
    def __init__(self, path: os.PathLike):
        super().__init__(path)
        self._query: str = None
        self.fields: dict[str, arcpy.Field] = {field.name: field for field in arcpy.ListFields(self.path)}
        self.fieldnames: list[str] = list(self.fields.keys())
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
        self.valid_fields = self.fieldnames + self.cursor_tokens
        self.queried: bool = False
        self._queried_count: int = 0
        self._updated: bool = False
        self.record_count: int = int(arcpy.management.GetCount(self.path).getOutput(0))
        self._oid_set: set[int] = set(self[self.OIDField])
        self.editor = self._get_editor() # sets a valid workspace
        self._iter = None
        return
    
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
        self._updated = True
        self.queried = True
        self._queried_count = len(self)
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
    
    def _handle_queries(self, kwargs):
        if 'where_clause' in kwargs:
            return f"({self query}) AND ({kwargs['where_clause']})"
        else:
            return self.query
    
    def _validate_fields(self, fields: list[str]) -> bool:
        """ Validate field list for cursors """
        if fields not in (["*"] , Table.ALL_FIELDS) and not all((field in self.valid_fields for field in fields)):
            return False
        return True
    
    def _get_editor(self):
        """ Get the editor of the table (walks up the directory tree until it finds a valid workspace)"""
        valid_workspace = False
        while not valid_workspace:
            try:
                with arcpy.da.Editor(self.workspace):
                    valid_workspace = True
            except RuntimeError:
                self.workspace = os.path.dirname(self.workspace)
        return arcpy.da.Editor(self.workspace)
    
    def _cursor(self, cur_type: str, fields: list[str]=ALL_FIELDS, **kwargs) -> arcpy.da.UpdateCursor | arcpy.da.SearchCursor | arcpy.da.InsertCursor:
        """ Internal cursor method to get cursor type
        """
        if fields is Table.ALL_FIELDS or fields == ["*"]: 
            fields = self.fieldnames
            
        if not self._validate_fields(fields): 
            raise ValueError(f"Fields must be in {self.valid_fields}")
        
        kwargs['where_clause'] = self._handle_queries(kwargs)
        
        if cur_type == "search": 
            return arcpy.da.SearchCursor(self.path, fields, **kwargs)
        
        if cur_type == "update":
            self._updated = True
            return arcpy.da.UpdateCursor(self.path, fields, **kwargs)
        
        if cur_type == "insert":
            self._updated = True
            return arcpy.da.InsertCursor(self.path, fields, **kwargs)
        
        raise ValueError(f"Invalid cursor type {cur_type}")
    
    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        yield from as_dict(self.search_cursor())
    
    def __next__(self) -> dict[str, Any]:
        if not self._iter:
            self._iter = as_dict(self.search_cursor())
        try:
            return next(self._iter)
        except StopIteration:
            self._iter = None
            raise StopIteration
        
    def __len__(self) -> int:
        if self.queried: return self._queried_count
        if not self._updated: return self.record_count
        self._updated = False
        self.record_count = int(arcpy.management.GetCount(self.path).getOutput(0))
        return self.record_count
    
    @overload
    def __getitem__(self, idx: int) -> Any: ...
    
    @overload
    def __getitem__(self, idx: str) -> Generator[Any, None, None]: ...
    
    @overload
    def __getitem__(self, idx: Iterable[int]) -> Generator[Any, None, None]: ...
    
    @overload
    def __getitem__(self, idx: Iterable[str]) -> Generator[Any, None, None]: ...
    
    def __getitem__(self, idx: int | str | Iterable[int] | Iterable[str]) -> Any:
        if isinstance(idx, int) and idx in self._oid_set:
            yield from as_dict(self.search_cursor(where_clause=f"{self.OIDField} = {idx}"))
            return

        if isinstance(idx, str) and idx in self.valid_fields:
            yield from ( value[idx] for value in as_dict(self.search_cursor([idx])) )
            return
        
        if isinstance(idx, str):
            raise KeyError(f"{idx} not in {self.valid_fields}")
        
        if isinstance(idx, Iterable) and all(field in self.valid_fields for field in idx):
            yield from as_dict(self.search_cursor(idx))
            return
            
        if isinstance(idx, Iterable) and all(isinstance(oid, int) for oid in idx):
            yield from as_dict(self.search_cursor(where_clause=f"{self.OIDField} IN ({','.join(str(i) for i in idx)})"))
            return
        
        raise ValueError(f"{idx} is invalid, either pass field, OID, or list of fields or list of OIDs ({self.valid_fields})")
    
    @overload
    def __setitem__(self, idx: int, val: Any) -> None: ...
    
    @overload
    def __setitem__(self, idx: str, val: Mapping[str, Any]) -> None: ...
    
    @overload
    def __setitem__(self, idx: str, val: Any) -> None: ...
    
    @overload
    def __setitem__(self, idx: Iterable, val: Iterable[Any]) -> None: ...
    
    def __setitem__(self, idx: int | str | Iterable[str], val: Mapping[str, Any] | Any) -> None:
        
        if (idx in self._oid_set) and isinstance(val, Mapping) and all(field in val.keys() for field in self.fieldnames):
            with self.editor:
                with self.update_cursor(list(val.keys()), where_clause=f"{self.OIDField} = {idx}") as cursor:
                    for _ in cursor: cursor.updateRow([val[field] for field in cursor.fields])
            return
        
        if isinstance(idx, str) and idx in self.valid_fields:
            with self.editor:
                with self.update_cursor([idx]) as cursor:
                    for _ in cursor: cursor.updateRow([val])
            return
        
        if isinstance(idx, Iterable) and all(field in self.valid_fields for field in idx):
            with self.editor:
                with self.update_cursor(idx) as cursor:
                    for _ in cursor: cursor.updateRow(val)
            return
        
        raise ValueError(f"{idx} not in {self.valid_fields} or index is out of range")
    
    @overload
    def __delitem__(self, idx: int) -> None: ...
    
    @overload
    def __delitem__(self, idx: str) -> None: ...
    
    @overload
    def __delitem__(self, idx: Iterable[str]) -> None: ...
    
    @overload
    def __delitem__(self, idx: Iterable[int]) -> None: ...
    
    def __delitem__(self, idx: int | str | Iterable[str] | Iterable[int]) -> str:
        if isinstance(idx, int):
            with self.editor:
                with self.update_cursor(where_clause=f"{self.OIDField} = {idx}") as cursor:
                    for _ in cursor: cursor.deleteRow()
            return
        
        if isinstance(idx, str) and idx in self.fieldnames:
            self.delete_field(idx)
            return
        
        if isinstance(idx, Iterable) and all(field in self.fieldnames for field in idx):
            for field in idx:
                self.delete_field(field, _update=False)
            self.update()
            return
         
        if isinstance(idx, Iterable) and all(oid in self._oid_set for oid in idx):
            with self.editor:
                with self.update_cursor(where_clause=f"{self.OIDField} IN ({','.join(idx)})") as cursor:
                    for _ in cursor: cursor.deleteRow()
            return
        
        raise KeyError(f"{idx} not in {self.valid_fields}")
    
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
    
    def add_field(self, field_name: str, **kwargs) -> None:
        """ Add a field to the table 
        field_name: name of the field to add
        kwargs: See arcpy.management.AddField for kwargs
        """
        arcpy.management.AddField(self.path, field_name, **kwargs)
        self.update()
        return
    
    def delete_field(self, field_name: str, _update=True) -> None:
        """ Delete a field from the table 
        field_name: name of the field to delete
        """
        arcpy.management.DeleteField(self.path, field_name)
        if _update: self.update()
        return
    
    def to_json(self, **kwargs) -> str:
        """ returns a json string of the Table/Features
        """
        out_file = arcpy.conversion.FeaturesToJSON(
            in_features=self.path, 
            format_json=True, 
            **kwargs)[0]
        json_string = open(out_file, 'rt').read()
        os.remove(out_file)
        return json_string
    
    def to_geo_json(self, **kwargs) -> str:
        """  returns a geojson string of the Table/Features
        """
        return self.to_json(geoJSON=True, **kwargs)
    
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
        self.valid_fields = self.fieldnames + self.cursor_tokens
        self.fieldnames[self.fieldnames.index(self.describe.shapeFieldName)] = "SHAPE@"
      
class ShapeFile(FeatureClass): ...

class FeatureDataset(DescribeModel): ...

class Workspace(DescribeModel):
    
    def __init__(self, path: os.PathLike, fc_filter: list[str]=None):
        super().__init__(path)
        
        self.fc_filter = fc_filter
        arcpy.env.workspace = self.path
        self.datasets: dict[str, FeatureDataset] = \
            {
                ds: FeatureDataset(os.path.join(self.path, ds)) 
                for ds in arcpy.ListDatasets()
            }
        print(f"Found Datasets: {len(self.datasets)}")
        self.featureclasses: dict[str, FeatureClass] = \
            {
                fc: FeatureClass(os.path.join(self.path, fc)) 
                for fc in arcpy.ListFeatureClasses()
                if fc in self.fc_filter
            }
        for ds in self.datasets.keys():
            self.featureclasses.update(
                {
                    fc: FeatureClass(os.path.join(self.path, ds, fc))
                    for fc in arcpy.ListFeatureClasses(feature_dataset=ds)
                    if fc in self.fc_filter
                }
            )
        print(f"Found FeatureClasses: {len(self.featureclasses)}")
        self.tables: dict[str, Table] = \
            {
                tbl: Table(os.path.join(self.path, tbl)) 
                for tbl in arcpy.ListTables()
                if tbl in self.fc_filter
            }
        print(f"Found Tables: {len(self.tables)}")
        return
    
    def __getitem__(self, idx: str) -> FeatureClass | Table | FeatureDataset:
        if idx in self.featureclasses: return self.featureclasses[idx]
        if idx in self.tables: return self.tables[idx]
        if idx in self.datasets: return self.datasets[idx]
        raise KeyError(f"{idx} not in {self.featureclasses.keys()} or {self.tables.keys()} or {self.datasets.keys()}")


def as_dict(cursor: arcpy.da.SearchCursor | arcpy.da.UpdateCursor) -> Generator[dict[str, Any], None, None]:
    """ Convert a search cursor or update cursor to a dictionary 
    cursor: search cursor or update cursor
    return: generator of dictionaries
    
    usage:
    >>> with table.search_cursor() as cursor:
    >>>     for row in as_dict(cursor):
    >>>         print(row)
    
    >>> with table.update_cursor() as cursor:
    >>>     for row in as_dict(cursor):
    >>>        cursor.updateRow([row[field] for field in table.fieldnames])
        
    """
    yield from ( dict(zip(cursor.fields, row)) for row in cursor )

if __name__ == "__main__":
    spans = FeatureClass(r"C:\Users\asimov\Desktop\Network Builder\Data\Ezee Fiber Katy South 1.1\lld_design.gdb\Design\Span")