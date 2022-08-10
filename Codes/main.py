# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import os
import pathlib
import sys
from typing import Any
#
from object import StreamProcessSet
from util import JSONCReader
from window import MainWindow
# -----------------------------------------------------------------------------


# Files
# -----------------------------------------------------------------------------
# Base folder
this_folder: pathlib.Path = pathlib.Path(
    rf'{os.path.abspath(os.path.dirname(sys.argv[0]))}'
)
#
streamlink_jsonc_file: pathlib.Path = this_folder / 'streamlink.jsonc'
streamlink_jsonc_obj: dict[str, Any] = JSONCReader.open_and_loads(
    streamlink_jsonc_file
)
del streamlink_jsonc_file
#
log_file: pathlib.Path = this_folder / 'streamlink.log'
#
del this_folder
# -----------------------------------------------------------------------------


# Main
# -----------------------------------------------------------------------------
sps: StreamProcessSet = StreamProcessSet(
    int(streamlink_jsonc_obj['portsFrom']), 16, streamlink_jsonc_obj, log_file, 
)
mw: MainWindow = MainWindow(sps)
mw.open()
del sps
# -----------------------------------------------------------------------------
