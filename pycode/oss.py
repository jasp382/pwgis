"""
Interact with Operating System
"""

import os

def os_name():
    import platform
    return str(platform.system())

def execmd(cmd):
    """
    Execute a command and provide information about the results
    """
    import subprocess
    
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    out, err = p.communicate()
    
    if p.returncode != 0:
        raise ValueError((
            'Message: Command execution ended with error\n'
            'Command was: {cmd}\n'
            'Output: {o}\n'
            'Error: {e}'
        ).format(
            cmd=cmd, o=out.decode('utf-8'), e=err.decode('utf-8')
        ))
    
    else:
        return out.decode('utf-8')


def mkdir(folder, randName=None, overwrite=True):
    """
    Create a new folder
    Replace the given folder if that one exists
    """
    
    if randName:
        import random
        chars = '0123456789qwertyuiopasdfghjklzxcvbnm'
        
        name = ''
        for i in range(10):
            name+=random.choice(chars)
        
        folder = os.path.join(folder, name)
    
    if os.path.exists(folder):
        if overwrite:
            import shutil
            
            shutil.rmtree(folder)
        else:
            raise ValueError(
                "{} already exists".format(folder)
            )
    
    os.mkdir(folder)
    
    return folder


def del_folder(folder):
    """
    Delete folder if exists
    """
    
    import shutil
    
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)


def lst_ff(w, file_format=None, filename=None, rfilename=None):
    """
    List the abs path of all files with a specific extension on a folder
    """
    
    from pycode import obj_to_lst
    
    # Prepare file format list
    if file_format:
        formats = obj_to_lst(file_format)
        
        for f in range(len(formats)):
            if formats[f][0] != '.':
                formats[f] = '.' + formats[f]
    
    # List files
    r = []
    for (d, _d_, f) in os.walk(w):
        r.extend(f)
        break
    
    # Filter files by format or not
    if not file_format:
        if not rfilename:
            t = [os.path.join(w, i) for i in r]
        else:
            t = [i for i in r]
    
    else:
        if not rfilename:
            t = [
                os.path.join(w, i) for i in r
                if os.path.splitext(i)[1] in formats
            ]
        else:
            t = [i for i in r if os.path.splitext(i)[1] in formats]
    
    # Filter by filename
    if not filename:
        return t
    
    else:
        filename = obj_to_lst(filename)
        
        _t = []
        for i in t:
            fn = fprop(i, 'fn') if not rfilename else i
            if fn in filename:
                _t.append(i)
        
        return _t


def lst_fld(w, name=None):
    """
    List folders path or name in one folder
    """
    
    foldersname = []
    for (dirname, dirsname, filename) in os.walk(w):
        foldersname.extend(dirsname)
        break
    
    if name:
        return foldersname
    
    else:
        return [os.path.join(w, fld) for fld in foldersname]


def fprop(__file, prop, forceLower=None, fs_unit=None):
    """
    Return some property of file

    prop options:
    * filename or fn - return filename
    """

    from pycode import obj_to_lst

    prop = obj_to_lst(prop)

    result = {}

    if 'filename' in prop or 'fn' in prop:
        fn, ff = os.path.splitext(os.path.basename(__file))

        result['filename'] = fn 

        if 'fileformat' in prop or 'fn' in prop:
            result['fileformat'] = ff
    
    elif 'fileformat' in prop or 'ff' in prop:
        result['fileformat'] = os.path.splitext(__file)[1]
    
    if 'filesize' in prop or 'fs' in prop:
        fs_unit = 'MB' if not fs_unit else fs_unit

        fs = os.path.getsize(__file)

        if fs_unit == 'MB':
            fs  = (fs / 1024.0) / 1024
        
        elif fs_unit == 'KB':
            fs = fs / 1024.0
        
        result['filesize'] = fs
    
    if len(prop) == 1:
        if prop[0] == 'fn':
            return result['filename']
        elif prop[0] == 'ff':
            return result['fileformat']
        elif prop[0] == 'fs':
            return result['filesize']
        else:
            return result[prop[0]]
    else:
        return result

