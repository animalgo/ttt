import json
import os

class Settings:

    def __init__(self):
        with open('settings.json') as f:
            s = json.load(f)
        self._s = s
        self._paths = self._join_paths()

    def _join_paths(self)->dict:
        
        s = self._s
        results_path = s['results_path']
        filenames = s['filenames']
        paths = {}
        for name,file in filenames.items():
            path = os.path.join(results_path,file)
            paths[name] = path
        
        return paths

    def path(self,name:str)->str:
        if name == 'results':
            return self._s['results_path']
        else:
            return self._paths[name]