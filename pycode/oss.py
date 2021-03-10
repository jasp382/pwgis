"""
Interact with Operating System
"""

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

