# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import dataclasses
import enum
import logging
import pathlib
import subprocess
from typing import Any, NamedTuple
# -----------------------------------------------------------------------------


# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(message)s',
    level=logging.DEBUG, 
    encoding='utf-8', 
)
logger: logging.Logger = logging.getLogger(__name__)

import threading
def asdf(proc: subprocess.Popen, port: int):
    for l in zxcv(proc):
        logger.info(f'({port}) {l.decode("utf-8", "ignore").strip()}')
        # logger.info(f'({port}) {l.strip()}')

def zxcv(proc: subprocess.Popen):
    while True:
        l = proc.stdout.readline()
        if l:
            yield l
        if not l and proc.poll() is not None:
            break
# -----------------------------------------------------------------------------

# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True, )
class StreamProcessSet:
    __port_fr: dataclasses.InitVar[int]
    __num_ports: dataclasses.InitVar[int]
    d: dict[str, Any]
    __processes: dict[int, StreamStatus | None] = dataclasses.field(
        init=False, default_factory=dict, 
    )
    __log_file: dataclasses.InitVar[pathlib.Path]

    def __post_init__(self, 
            __ports_fr: int, __num_ports: int, __log_file: pathlib.Path, 
            ) -> None:
        for i in range(__ports_fr, __ports_fr + __num_ports):
            self.__processes[i] = None
        del i
        h = logging.FileHandler(
            filename=__log_file, encoding='utf-8', 
        )
        h.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        h.setLevel(logging.DEBUG)
        logger.addHandler(h)

    @property
    def port_fr(self) -> int:
        return [p for p in self.__processes.keys()][0]

    @property
    def num_ports(self) -> int:
        return len(self.__processes)

    def start(self, port: int, stream: Stream) -> None:
        if self.__processes[port] is not None:
            self.__processes[port].proc.kill()
            self.__processes[port].th.join()
            self.__processes[port] = None
        #
        args: list[str] = []
        args.append(self.d['streamlinkPath'])
        args.extend(self.d['streamlinkOptions']['_common'])
        if stream.site is SiteCategory.NICONICO:
            args.extend(self.d['streamlinkOptions']['nicolive'])
            args.append(rf'--url https://live.nicovideo.jp/watch/{stream.channel}')
        elif stream.site is SiteCategory.TWITCH:
            args.extend(self.d['streamlinkOptions']['twitch'])
            args.append(rf'--url https://www.twitch.tv/{stream.channel}')
        elif stream.site is SiteCategory.YOUTUBE:
            args.extend(self.d['streamlinkOptions']['youtube'])
            args.append(rf'--url https://www.youtube.com/{stream.channel}/live')
        args.append(f'--player-external-http-port {port}')
        p: subprocess.Popen =  subprocess.Popen(
            ' '.join(args), 
            shell=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            # encoding='utf-8', 
            # errors='ignore', 
        )
        self.__processes[port] = StreamStatus(
            stream, 
            p, 
            threading.Thread(target=asdf, args=[p, port])
        )
        self.__processes[port].th.start()

    def stop(self, port: int) -> None:
        if self.__processes[port] is not None:
            self.__processes[port].proc.kill()
            self.__processes[port].th.join()
            self.__processes[port] = None

    def refresh(self) -> dict[int, ProcessStatusCategory]:
        d: dict[int, ProcessStatusCategory] = {}
        for k, v in self.__processes.items():
            if v is None:
                d[k] = ProcessStatusCategory.NOT_RUNNING
                self.__processes[k] = None
                continue
            if v.proc.poll() is None:
                d[k] = ProcessStatusCategory.RUNNING
            else:
                d[k] = ProcessStatusCategory.NOT_RUNNING
                self.__processes[k] = None
            # try:
            #     out, _ = v.proc.communicate(timeout=0.25)
            #     if out is not None:
            #         outs: list[str] = out.decode().strip().split('\r\n')
            #         for o in outs:
            #             logger.info(o)
            # except subprocess.TimeoutExpired:
            #     pass
        return d

    def kill_all(self) -> None:
        pass
        for v in self.__processes.values():
            if v is not None:
                v.proc.kill()
                v.th.join()
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True, )
class Stream:
    outline: str
    site: SiteCategory
    channel: str
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class StreamStatus(NamedTuple):
    stream: Stream
    proc: subprocess.Popen[bytes]
    th: threading.Thread
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@enum.unique
class ProcessStatusCategory(enum.Enum):
    '''(列挙帯)Streamlink実行プロセスの状態'''
    RUNNING = '動作中'
    NOT_RUNNING = '停止中'
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@enum.unique
class SiteCategory(enum.Enum):
    '''(列挙帯)ストリーミングサイト'''
    TWITCH = 'ツイッチ'
    YOUTUBE = 'ユーチューブ'
    NICONICO = 'ニコニコ'
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
