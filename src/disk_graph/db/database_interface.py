class database_interface:
    def __init__(name=''):
        raise NotImplementedError(
            f"{type(self).__name__}: Constructor was not implemented."
        )
    
    def createTables():
        raise NotImplementedError(
            f"{type(self).__name__}: createTables function was not implemented."
        )
    
    def getTableColumns(name):
        raise NotImplementedError(
            f"{type(self).__name__}: getColumns function was not implemented."
        )