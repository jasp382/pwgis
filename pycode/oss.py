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

