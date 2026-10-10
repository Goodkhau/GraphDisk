class database_interface:
    def __init__(name=''):
        raise NotImplementedError(
            self.notCreatedMessage(self._testMethodName)
        )
    
    def notCreatedMessage(function_name):
        return f"{type(self).__name__}: {function_name} was not implemented."
    
    def createTables():
        raise NotImplementedError(
            self.notCreatedMessage(self._testMethodName)
        )
    
    def getTableColumns(name):
        raise NotImplementedError(
            self.notCreatedMessage(self._testMethodName)
        )

    def createNodeColumns(new_columns: list[dict]):
        raise NotImplementedError(
            self.notCreatedMessage(self._testMethodName)
        )