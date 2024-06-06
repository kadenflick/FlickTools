import arcpy
import os
import shutil
import json


class Parameters(object):
    """ Parameters class to store the parameters of a tool """
    def __init__(self, parameters: list) -> None:
        self._parameters = parameters
        for parameter in parameters:
            self.__dict__[parameter.name] = parameter
        return
    
    def __iter__(self):
        for _, value in self._parameters.items():
            yield value
        return
    
def sanitize_filename(filename: str) -> str:
    """ Sanitize a filename """
    return "".join([char for char in filename if char.isalnum() or char in [" ", "_", "-"]])