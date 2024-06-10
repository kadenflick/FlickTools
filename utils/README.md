TODO:

[ ] - Add explicit caching to Table object with `cache()` and `clear_cache()` methods and remove all implicit caching in data update functions. Instead invalidate the cache on update and raise a CacheError when the cache isn't explicitly cleared and rebuilt after modification operations or when the row count stored in the table object doesn't match the row count of a search cursor. This will still possibly cause issues if a user modifies a table with another Table object instance, but that will be addressed in a later update.

[ ] - Update `get_rows` to iterate over cached data if it is present

[ ] - If cache is present, calls to query property will by default update the cache

[ ] - Test if running update operations on cached data and not writing changes until a `commit()` call is made is viable. This could come into conflict with the query property overwriting the cache, so we might need to have a secondary queried cache that maps to the main cache. Possibly implement Caching in a separate class.

[ ] - Allow creation of Table objects with valid workspace paths thatsont currently exist. Overload the constructor to try and create an object in the workspace with the specified data type based on the subclass constructor that is called. This will likely have to be implemented in each subclass before `super().__init__()` call because the arcpy constructor function for each type require different parameters. (e.g. FeatureClass(<path>, shapeType='Polygon', fields=[<Field>, ...])