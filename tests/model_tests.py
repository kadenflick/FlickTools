import utils.models as models

TEST_PATH = r"C:\Users\hwelch\Desktop\shp\parcels.shp"

def test_model():
    
    shapefile = models.ShapeFile(TEST_PATH)
    
    print("-----TESTING SHAPEFILE-----")
    print("\t Shapefile str(): ", str(shapefile))
    print("\t Shapefile repr(): ", repr(shapefile))
    print("\t Shapefile len():", len(shapefile))
    print("\t Shapefile shapefile[idx]: ", str(shapefile[0])[0:10], "...")
    print("\t Shapefile add_field(): ", shapefile.add_field("test_field", "TEXT"))
    print("\t Shapefile update(): ", shapefile.update())
    if 'test_field' not in shapefile.fieldnames:
        print("\t Shapefile add_field() or update() failed")
    print("\t Shapefile append(): ")
    row_template = dict(zip(shapefile.fieldnames, [None for i in range(len(shapefile.fieldnames))]))
    row_template['test_field'] = 'test_value'
    shapefile.append(list(row_template.values()))
    print("\t Shapefile Assignment shapefile[idx] = ...: ")
    print("\t Shapefile Deletion del shapefile[idx]: ")
    