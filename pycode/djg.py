"""
Deal with files
"""

def save_file(save_fld, _file):
    """
    Store a uploaded file in a given folder
    """ 
    
    import os
    
    file_out = os.path.join(save_fld, _file.name)
    with open(file_out, 'wb+') as destination:
        for chunk in _file.chunks():
            destination.write(chunk)
    
    return file_out


def save_geodata(request, field_tag, folder, return_only_one_file=None):
    """
    Receive a file with vectorial geometry from a form field:
    
    Store the file in the server
    
    IMPORTANT: this method will only work if the FORM that is receiving the 
    files allows multiple files
    """
    
    import os
    
    files = request.FILES.getlist(field_tag)
    
    for f in files:
        save_file(folder, f)
    
    # List geo files
    gfiles = []
    for f in files:
        name, ff = os.path.splitext(f.name)

        if ff == '.shp' or ff == '.tif':
            if return_only_one_file:
                return os.path.join(folder, f.name)
            
            else:
                gfiles.append(os.path.join(
                    folder, f.name
                ))
    
    return gfiles
