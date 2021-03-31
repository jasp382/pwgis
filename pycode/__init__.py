"""
Python package to support Programming for WebGIS classes
"""


def obj_to_lst(obj):
    """
    A method uses a list but the user gives other type of object
    
    This method will see if the object is not a list and convert it to a list
    """

    return obj if type(obj) == list else [obj] if obj != None else None

