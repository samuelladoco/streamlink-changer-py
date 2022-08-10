# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import chardet
import collections
import json
import pathlib
import re
from typing import Any, ClassVar, Union
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class JSONCReader:
    """JSONCファイル読み込むクラス(クラスメソッドのみ)"""

    s_dummy_for_end: ClassVar[str] = 'dummyForEnd'

    @classmethod
    def open_and_loads(cls, file: pathlib.Path | str) -> dict[str, Any]:
        """ファイルをパースして内容を辞書形式で返す

        Parameters
        ----------
        file : pathlib.Path | str
            ファイルのパス

        Returns
        -------
        dict[str, Any]
            ファイルの内容を辞書形式にしたもの(ダミー文字列は含まれない)
        """

        s: str = ''
        with open(file, 'r', encoding=TextFileEncodingEstimator.do(file)) as f:
            s = f.read()
        del f
        d: dict[str, Any] = json.loads(re.sub(r'/\*[\s\S]*?\*/|//.*', '', s))
        q: collections.deque[Union[list[Any], dict[str, Any]]] = collections.deque()
        q.append(d)
        while len(q) > 0:
            ld: Union[list[Any], dict[str, Any]] = q.popleft()
            if type(ld) is list:
                while cls.s_dummy_for_end in ld:
                    ld.remove(cls.s_dummy_for_end)
                q.extend(
                    [e for e in ld if type(e) is dict or type(e) is list]
                )
            elif type(ld) is dict and cls.s_dummy_for_end in ld:
                del ld[cls.s_dummy_for_end]
                q.extend(
                    [v for v in ld.values() if type(v) is dict or type(v) is list]
                )
            del ld
        del q
        return d
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class TextFileEncodingEstimator:
    """テキストファイルのエンコーディングを推定するクラス(クラスメソッドのみ)"""

    @classmethod
    def do(cls, file: pathlib.Path | str) -> str:
        """テキストファイルのエンコーディングを推定する

        Parameters
        ----------
        file : pathlib.Path | str
            ファイルのパス

        Returns
        -------
        str
            推定したエンコーディングの名称
        """

        str_encoding: str = ''
        with open(file, 'rb') as f_b:
            str_encoding = chardet.detect(f_b.read())['encoding']
        del f_b
        return str_encoding
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
