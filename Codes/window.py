# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import csv
import dataclasses
import PySimpleGUI as sg
#
from object import StreamProcessSet, Stream, SiteCategory, ProcessStatusCategory
from util import TextFileEncodingEstimator
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclasses.dataclass()
class MainWindow:
    """メインウィンドウ"""

    sps: StreamProcessSet
    ports: dict[int, int] = dataclasses.field(
        init=False, default_factory=dict, compare=False, 
    )
    __window: sg.Window = dataclasses.field(
        init=False, compare=False, 
    )

    def open(self) -> None:
        ls: list[list[sg.Any]] = [
            [
                sg.Button(button_text='状況を更新する', key='refresh', ),  
                sg.Button(button_text='ファイルを開く', key='open_popup_get_file', ), 
            ], 
        ]
        #
        fs: list[sg.Frame] = []
        for i in range(1, self.sps.num_ports):
            self.ports[i] = self.sps.port_fr - 1 + i
            fs.append(
                (Frame(i, self.ports[i], True if i < 4 else False)).get()
            )
            if i % 3 == 0 or i == self.sps.num_ports:
                ls.append(fs)
                fs = []
        del i

        self.__window = sg.Window('', ls)

        while True:
            evs: tuple[str | None, dict[str, str]] = self.__window.read(timeout=2000)
            e: str | None = evs[0]
            vs: dict[str, str] = evs[1]
            del evs
            #
            if e == 'refresh' or e == '__TIMEOUT__':
                self.__refresh()
            #
            if e == 'open_popup_get_file':
                f_str: str = sg.popup_get_file('ファイルを開く')
                if f_str is None:
                    continue
                    #
                with open(
                        file=f_str, mode='r', 
                        encoding=TextFileEncodingEstimator.do(f_str)
                        ) as f:
                    rd = csv.reader(f, skipinitialspace=True)
                    num_streams: int = 3
                    for r in rd:
                        num_streams = int(len(r) / 3)
                        break
                    del r
                    #
                    rows: dict[int, list[list[str]]] = {
                        i : [] 
                        for i in range(1, num_streams + 1)
                    }
                    for r in rd:
                        for i in range(1, num_streams + 1):
                            rows[i].append(r[(i - 1) * 3:(i - 1) * 3 + 3])
                        del i
                    del r
                    #
                    for i in range(1, self.sps.num_ports):
                        if i <= num_streams:
                            self.__window[f'table_{i}'].update(values=rows[i])
                            self.__window[f'frame_{i}'].update(visible=True)
                        else:
                            self.__window[f'table_{i}'].update(values=[[]])
                            self.__window[f'frame_{i}'].update(visible=False)
                    del i
                    del num_streams
                    del rows
                del f
            #
            if e is not None and e.startswith('start_'):
                i: int = int(e.split('_')[1])
                if len([sc for sc in SiteCategory if sc.value is vs[f'category_{i}']]) == 0:
                    sg.popup('サイト名が空です')
                    self.__refresh()
                    continue
                s: SiteCategory = [sc for sc in SiteCategory if sc.value is vs[f'category_{i}']][0]
                c: str = vs[f'channel_{i}']
                if len(c.strip()) > 0:
                    self.sps.start(self.ports[i], Stream('', s, c))
                else:
                    sg.popup('チャンネル名が空です')
                    self.__refresh()
                    continue
                del i, s, c
                self.__refresh()
            #
            if e is not None and e.startswith('stop_'):
                i: int = int(e.split('_')[1])
                self.sps.stop(self.ports[i])
                self.__refresh()
                del i
            #
            if e is not None and e.startswith('up_'):
                self.__refresh()
                i: int = int(e.split('_')[1])
                if self.__window[f'status_{i}'].DisplayText == f'{ProcessStatusCategory.NOT_RUNNING.value}':
                    js: list[int] = self.__window[f'table_{i}'].SelectedRows
                    if len(js) > 0:
                        r: list[str] = self.__window[f'table_{i}'].Values[js[0]]
                        if len(r) >= 3:
                            self.__window[f'outline_{i}'].update(value=r[0])
                            self.__window[f'category_{i}'].update(value=r[1])
                            self.__window[f'channel_{i}'].update(value=r[2])
                        del r
                    del js
                del i
            # 
            if e is None:
                self.sps.kill_all()
                break

        self.__window.close()

    def __refresh(self) -> None:
        d: dict[int, ProcessStatusCategory] = self.sps.refresh()
        for k, v in d.items():
            if len([ii for ii, pp in self.ports.items() if pp == k]) == 0:
                continue
            i: int = [ii for ii, pp in self.ports.items() if pp == k][0]
            self.__window[f'status_{i}'].update(value=f'{v.value}')
            if v is ProcessStatusCategory.RUNNING:
                self.__window[f'start_{i}'].update(disabled=True)
                self.__window[f'stop_{i}'].update(disabled=False)
                self.__window[f'category_{i}'].update(disabled=True)
                self.__window[f'channel_{i}'].update(disabled=True)
                self.__window[f'channel_{i}'].update(text_color=f'#999999')
                self.__window[f'up_{i}'].update(disabled=True)
            elif v is ProcessStatusCategory.NOT_RUNNING:
                self.__window[f'start_{i}'].update(disabled=False)
                self.__window[f'stop_{i}'].update(disabled=True)
                self.__window[f'category_{i}'].update(disabled=False)
                self.__window[f'channel_{i}'].update(disabled=False)
                self.__window[f'channel_{i}'].update(text_color=f'#000000')
                self.__window[f'up_{i}'].update(disabled=False)
            del i
            pass
        del k, v
        del d

# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
@dataclasses.dataclass()
class Frame:
    no: int
    port: int = dataclasses.field(compare=False, )
    is_visible: bool = dataclasses.field(compare=False, )
    __layout: list[list[sg.Any]] = dataclasses.field(
        init=False, default_factory=list, compare=False,
    )

    def __post_init__(self) -> None:
        self.__layout.extend([
            [
                sg.Text(
                    text=f'状況：', 
                ), 
                sg.Text(
                    text=f'{ProcessStatusCategory.NOT_RUNNING.value}', 
                    key=f'status_{self.no}'
                ), 
                sg.Button(
                    button_text='起動する', 
                    key=f'start_{self.no}', 
                    disabled=False, 
                ), 
                sg.Button(
                    button_text='停止する', 
                    key=f'stop_{self.no}', 
                    disabled=True, 
                ), 
            ], 
            [
                sg.Text(
                    text='', 
                    size=(12 + 2, 1), 
                    key=f'outline_{self.no}', 
                ), 
                sg.Combo(
                    size=(12, 1), 
                    key=f'category_{self.no}', 
                    values=[sc.value for sc in SiteCategory], 
                    default_value=SiteCategory.TWITCH.value, 
                    readonly=True, 
                ), 
                sg.InputText(
                    size=(24, 1), 
                    key=f'channel_{self.no}', 
                )

            ], 
            [
                sg.Text(text=f'', size=(20, 0)), 
                sg.Button(
                    button_text='↑', 
                    size=(4, 1), 
                    key=f'up_{self.no}', 
                ), 

            ], 
            [
                sg.Table(
                    values=[
                        [
                            "", "", "", 
                        ]
                    ], 
                    headings=['概要', 'サイト', 'チャンネル', ], 
                    col_widths=[12 + 2, 10 + 2, 20], 
                    auto_size_columns=False, 
                    text_color='#000000', 
                    background_color='#cccccc', 
                    alternating_row_color='#ffffff', 
                    header_text_color = '#0000ff', 
                    header_background_color='#cccccc', 
                    key=f'table_{self.no}', 
                )
            ]
        ])

    def get(self) -> sg.Frame:
        return sg.Frame(
            title=f'Stream {self.no} ({self.port})', 
            layout=self.__layout, 
            visible=self.is_visible, 
            key=f'frame_{self.no}', 
        )
# ----------------------------------------------------------------------

# -----------------------------------------------------------------------------
