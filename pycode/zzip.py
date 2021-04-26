"""
Compress files with Python
"""


def zip_files(lst_files, zip_file):
    """
    Zip all files in the lst_files
    """
    
    import zipfile
    import os
    
    __zip = zipfile.ZipFile(zip_file, mode='w')
    
    for f in lst_files:
        __zip.write(f, os.path.relpath(f, os.path.dirname(zip_file)),
                    compress_type=zipfile.ZIP_DEFLATED)
    
    __zip.close()

    return zip_file

