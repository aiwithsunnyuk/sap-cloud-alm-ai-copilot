from enum import Enum


class CalmDataSource(str, Enum):
    SYNTHETIC = "synthetic"
    SAP = "sap"
