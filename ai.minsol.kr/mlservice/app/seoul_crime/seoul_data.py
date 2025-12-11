from dataclasses import dataclass
import pandas as pd
from pathlib import Path

@dataclass

class SeoulData(object): 

    _fname: str = '' # file name
    _dname: str = str(Path(__file__).parent / 'data') # data path
    _sname: str = str(Path(__file__).parent / 'save') # save path
    _cctv: pd.DataFrame = None
    _crime: pd.DataFrame = None
    _pop: pd.DataFrame = None


    @property
    def fname(self) -> str: return self._fname

    @fname.setter
    def fname(self, fname): self._fname = fname

    @property
    def dname(self) -> str: return self._dname

    @dname.setter
    def dname(self, dname): self._dname = dname

    @property
    def sname(self) -> str: return self._sname

    @sname.setter
    def sname(self, sname): self._sname = sname

    @property
    def cctv(self) -> pd.DataFrame: return self._cctv

    @cctv.setter
    def cctv(self, cctv): self._cctv = cctv

    @property
    def crime(self) -> pd.DataFrame: return self._crime

    @crime.setter
    def crime(self, crime): self._crime = crime

    @property
    def pop(self) -> pd.DataFrame: return self._pop

    @pop.setter
    def pop(self, pop): self._pop = pop

