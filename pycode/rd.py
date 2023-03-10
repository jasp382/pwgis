"""
Read Data
"""

def tbl_to_obj(tblFile, sheet=None, useFirstColAsIndex=None,
              _delimiter=None, encoding_='utf8', output='df',
              fields=None, colsAsArray=None):
    """
    Table File to Pandas DataFrame
    
    output Options:
    - df;
    - dict;
    - array;
    """
    
    from pycode.oss import fprop
    
    fFormat = fprop(tblFile, 'ff')
    
    if fFormat == '.dbf':
        """
        Convert dBase to Pandas Dataframe
        """
        
        from simpledbf import Dbf5
        
        dbfObj = Dbf5(tblFile)
        
        tableDf = dbfObj.to_dataframe()
    
    elif fFormat == '.ods':
        """
        ODS file to Pandas Dataframe
        """
        
        import pandas
        from pyexcel_ods import get_data
        
        if not sheet:
            raise ValueError("You must specify sheet name when converting ods files")
        data = get_data(tblFile)[sheet]
        
        tableDf = pandas.DataFrame(data[1:], columns=data[0])
    
    elif fFormat == '.xls' or fFormat == '.xlsx':
        """
        XLS to Pandas Dataframe
        """
        
        import pandas
        from pycode import obj_to_lst
        
        sheet = 0 if not sheet else sheet
        
        indexCol = 0 if useFirstColAsIndex else None
        
        tableDf = pandas.read_excel(
            tblFile, sheet, index_col=indexCol,
            encoding='utf-8', dtype='object',
            usecols=obj_to_lst(fields) if fields != "ALL" else None
        )
    
    elif fFormat == '.txt' or fFormat == '.csv':
        """
        Text file to Pandas Dataframe
        """
        
        import pandas
        
        if not _delimiter:
            raise ValueError(
                "You must specify _delimiter when converting txt files"
            )
        
        tableDf = pandas.read_csv(
            tblFile, sep=_delimiter, low_memory=False,
            encoding=encoding_
        )
    
    else:
        raise ValueError('{} is not a valid table format!'.format(fFormat))
    
    if fields:
        from pycode import obj_to_lst
        
        fields = obj_to_lst(fields)
        if fields:
            delCols = []
            for fld in list(tableDf.columns.values):
                if fld not in fields:
                    delCols.append(fld)
            
            if delCols:
                tableDf.drop(delCols, axis=1, inplace=True)
    
    if output != 'df':
        if output == 'dict':
            orientation = "index" if not colsAsArray else "list"
        
        elif output == 'array':
            tableDf["FID"] = tableDf.index
            
            orientation = "records"
        
        tableDf = tableDf.to_dict(orient=orientation)
    
    return tableDf


def imgsrc_to_num(img, flatten=None, with_nodata=True):
    """
    Convert Raster Source to Numpy Array
    """

    import numpy as np

    if not flatten and with_nodata:
        return img.ReadAsArray()
    elif flatten and with_nodata:
        return img.ReadAsArray().flatten()
    elif flatten and not with_nodata:
        bnd = img.GetRasterBand(1)
        no_val = bnd.GetNoDataValue()
        values = img.ReadAsArray().flatten()

        return np.delete(values, np.where(values==no_val), None)
    else:
        bnd = img.GetRasterBand(1)
        no_val = bnd.GetNoDataValue()
        values = img.ReadAsArray()

        return np.delete(values, np.where(values==no_val), None)


def rst_to_array(r, flatten=False, with_nodata=True):
    """
    Convert Raster image to numpy array
    
    If flatten equal a True, the output will have a shape of (1, 1).
    
    If with_nodata equal a True, the output will have the nodata values
    """
    
    from osgeo import gdal
    
    img = gdal.Open(r)

    return imgsrc_to_num(img, flatten=flatten, with_nodata=with_nodata)

