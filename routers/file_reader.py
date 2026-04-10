import pathlib
from pathlib import Path
from typing import Optional, Union
import warnings
import json


def read_file(file_path: Union[str, pathlib.PosixPath], file_type: str = None) -> Optional[str]:
    '''
    Safely read files without crashing.
    Inputs:
        `file_path`: either a string of a pathlib Path that can be relative or absolute
        `file_type`: how the file should be interpreted and returned. By default this is just returned as a normal str but can also be "json" which returns as a dict

    Outputs:
        returns either a string, a dict, or in the case that the file is not found, None.

    '''
    try:
        file_data = file_path.read_text(encoding="utf-8")
    except:
        warnings.warn(f'returning None as unable to find file: {file_path.resolve()}')
        return None

    if file_type == None:
        return file_data
    elif file_type == 'json':
        if file_data.strip() == '':
            warnings.warn(f'json file is empty so returning none to avoid crash: {file_path.resolve()}')
            return None
        else:
            return json.loads(file_data)
    else:
        raise ValueError(f'unable to interpret file_type: {file_type}')


# testing
if __name__ == "__main__":
    #print(read_file(Path('file_reader.py'))) #pass
    #print(read_file(Path('file_reader.py'), 'json')) #fail
    #print(read_file(Path('file_reader.py'), 'jason')) #fail
    #print(read_file(Path('file_reader'))) #fail
    #print(read_file(Path('*'))) #fail
    #print(read_file(Path('../data/main_notifications.json'), 'json')) #pass
    print(read_file(Path('../data/main_notifications.json'), 'jason')) #fail
