from abc import ABC, abstractmethod

class database_interface(ABC):
    def __init__(self, name: str = ''):
        pass

    @abstractmethod
    def createTables(self):
        pass

    @abstractmethod
    def getTableColumns(self, name: str):
        pass

    @abstractmethod
    def createNodeColumns(self, new_columns: list[dict]):
        pass