import argparse
import glob
import sys
import subprocess
import os
import xml.etree.ElementTree as ET
import datetime
from tqdm import tqdm

# メイン
def main():

    # 引数を取得
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('folder',  help='WindowsUpdateのログ（.etl）が存在するフォルダを指定してください。')
    arg_parser.add_argument('-o', '--outfolder', default='.', help='出力先フォルダを指定してください。')
    args = arg_parser.parse_args()

    # ログファイルの新規作成
    logfile = args.outfolder + '/ParsedWindowsUpdate.log'
    text = '日時\tプロセスID\tスレッドID\tコンポーネント\tイベントデータ'
    make_file(logfile, text)

    # 指定されたフォルダからetlファイルを取得
    etls = glob.glob(args.folder+'/*.etl')
    if not etls:
        sys.exit('etlファイルが見つかりません。\nフォルダパスは正しく指定していますか？')
    
    # etlファイルを1つずつ解析していく
    for etl in tqdm(etls):
        tmp_xml = etl_to_xml(etl)
        analyze_xml(tmp_xml, logfile)
        os.remove(tmp_xml)
    print('パース完了！')


# etlファイルをXMLに変換
def etl_to_xml(etl):

    tmp_xml = etl[:-3]
    tmp_xml = tmp_xml + 'xml'

    # 実行するコマンド
    cmd = 'netsh trace convert input="{}" output="{}" dump=xml overwrite=yes'.format(etl, tmp_xml)

    # netshコマンドの実行
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='shift-jis')
    if proc.returncode != 0:
        print(proc.stdout)
        os.remove(tmp_xml)
        sys.exit('etlファイルの変換に失敗しました。↑の入力ファイルの中身が正しいかチェックしてください。\n')
    return tmp_xml


# XMLの解析
def analyze_xml(tmp_xml, logfile):
    tree = ET.parse(tmp_xml)
    root = tree.getroot()

    # 名前空間の設定
    ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
    for event in root:
        system = event.find('ns:System', ns)

        # プロバイダー名がWUTraceLoggingの場合だけ解析
        if system.find('ns:Provider', ns).get('Name') == 'WUTraceLogging':
            
            # 日時の取得
            # タイムゾーンが +08:59 の場合は1秒プラスする
            time = system.find('ns:TimeCreated', ns).get('SystemTime')
            try:
                dt = datetime.datetime.fromisoformat(time)
                if time[-6:] == '+08:59':
                    dt = dt + datetime.timedelta(minutes=1)
                time = dt.strftime('%Y/%m/%d %H:%M:%S.%f')
            except ValueError as e:
                sys.exit(f'ISO 8601の形式に対応していない可能性があります。Pythonのバージョンは3.11以降を利用してください。\n{e}' )
            
            # プロセスIDとスレッドIDの取得
            pid = system.find('ns:Execution', ns).get('ProcessID')
            tid = system.find('ns:Execution', ns).get('ThreadID')

            # コンポーネントの取得
            rendering = event.find('ns:RenderingInfo', ns)
            task = rendering.find('ns:Task', ns).text

            # EventDataの中身を取得
            eventdata = event.find('ns:EventData', ns)
            detail = eventdata.find('ns:Data', ns).text

            # ログファイルに追記
            text = '\n' + time + '\t' + pid + '\t' + tid + '\t' + task + '\t' + detail
            append_file(logfile, text)

# ファイルの新規作成
def make_file(outfile, text):
    with open(outfile, 'w', encoding='utf-8-sig') as f:
        f.write(text)

# 既存のファイルに追記
def append_file(outfile, text):
    with open(outfile, 'a', encoding='utf-8-sig') as f:
        f.write(text)


if __name__ == '__main__':
    main()