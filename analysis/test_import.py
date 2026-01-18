print("Start import")
try:
    import pandas
    print("pandas ok")
    import numpy
    print("numpy ok")
    import semopy
    print("semopy ok")
    import scipy
    print("scipy ok")
except Exception as e:
    print(f"Import failed: {e}")
