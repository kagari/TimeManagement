import sys
import os
import time
from datetime import datetime
from typing import Tuple

DATA_DIR = './data/'
CONFIG_FNAME = '.conf'  # 現在の稼働ファイル名を保存するファイル


def read_config_data() -> str:
    """設定ファイルの情報を取得する

    Returns:
        fpath (str): 現在の勤怠ログの保存
    """
    confpath = DATA_DIR+CONFIG_FNAME
    if not os.path.isfile(confpath):
        exit('config file not exist.')
    with open(confpath, 'r') as f:
        return f.read().split('\n')[0]


def logdata_count(fpath: str) -> Tuple[bool, bool, int, int]:
    """勤怠ログファイルに保存されている情報を返す
    出退勤のログは1つ以上あることを想定していない

    Args:
        fpath (str): 退勤ログデータのファイル名

    Returns:
        started (bool): 出勤ログがあるか
        ended (bool): 退勤ログがあるか
        nbreak (int): 休憩開始の数
        nback (int): 休憩終了の数
    """
    started = False
    ended = False
    nbreak = 0  # 休憩開始の数
    nback = 0   # 休憩終了の数
    with open(fpath, 'r') as f:
        for line in f.read().split('\n')[:-1]:  # 最後は空行なので無視
            _t, _command = line.split(',')
            if _command == '"start"':
                started = True
            elif _command == '"end"':
                ended = True
            elif _command == '"break"':
                nbreak += 1
            elif _command == '"back"':
                nback += 1
    return started, ended, nbreak, nback


def _start():
    # 1日1回実行されるはず
    # スタート日時でinboxにファイルを作成
    # 休憩などの情報はそのファイルに出力する
    t = time.time()

    # 前回のログデータが稼働終了で終わっているか確認する
    if os.path.isfile(DATA_DIR+CONFIG_FNAME):
        fpath = read_config_data()
        _, ended, _, _ = logdata_count(fpath)
        if not ended:
            exit('前回稼働時の退勤打刻がされていません。\n退勤打刻を行なってください。')

    dt = datetime.fromtimestamp(int(t))
    directory = f'{DATA_DIR}inbox/{dt.year}/{dt.month:02d}/'
    fname = f'{dt.day:02d}.csv'
    if os.path.isfile(directory+fname):
        exit('同日に稼働した形跡があります。')
    os.makedirs(directory, exist_ok=True)

    with open(DATA_DIR+CONFIG_FNAME, 'w') as f:
        f.write(directory+fname)

    with open(directory+fname, 'w') as f:
        f.write('"time","command"\n')
        f.write(f'{t},"start"\n')


def _end():
    t = time.time()
    fpath = read_config_data()

    _, ended, nbreak, nback = logdata_count(fpath)
    if ended:
        # 既に退勤が押されている場合はエラー
        exit('既に退勤しています。')
    if nbreak != nback:
        exit('休憩の終了が打刻されていません。\n終了打刻をして下さい。')

    with open(fpath, 'a') as f:
        f.write(f'{t},"end"\n')


def _break():
    t = time.time()
    fpath = read_config_data()

    _, ended, nbreak, nback = logdata_count(fpath)
    if ended:
        # 既に退勤が押されている場合はエラー
        exit('既に退勤しています。')
    if nbreak != nback:
        exit('休憩の終了が打刻されていません。\n終了打刻をして下さい。')

    with open(fpath, 'a') as f:
        f.write(f'{t},"break"\n')


def _back():
    t = time.time()
    fpath = read_config_data()

    _, ended, nbreak, nback = logdata_count(fpath)
    if ended:
        # 既に退勤が押されている場合はエラー
        exit('既に退勤しています。')
    if nbreak-1 != nback:
        exit('休憩の開始が打刻されていません。')

    with open(fpath, 'a') as f:
        f.write(f'{t},"back"\n')


SUBCOMMANDS = {
    'start': _start,  # 稼働開始
    'end'  : _end,    # 稼働終了
    'break': _break,  # 休憩開始
    'back' : _back    # 休憩終了
}

if __name__ == '__main__':
    subcommand = sys.argv[1]
    if subcommand not in SUBCOMMANDS:
        exit(f'{subcommand} not in start, end, break, back.')
    SUBCOMMANDS[subcommand]()
