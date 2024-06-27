# WindowsUpdateLogParser
## ツール概要
本ツールは日本語対応させたWindows Updateログ（.etlファイル）のパーサです。  

[Windows Updateのログファイル](https://learn.microsoft.com/ja-jp/windows/deployment/update/windows-update-logs)はPowerShellの[Get-WindowsUpdateLogコマンド](https://learn.microsoft.com/ja-jp/powershell/module/windowsupdate/get-windowsupdatelog?view=windowsserver2022-ps&viewFallbackFrom=win10-ps&preserve-view=tru)でテキスト形式に変換可能ですが、マルチバイトには対応していないようで日本語は文字化けしてしまいます。  
そこで、ログファイルに含まれる日本語の文字化けを防ぎ、テキスト形式に変換する本ツールを開発しました。  

本ツールは以下のようなシンプルな流れで変換処理を行っています。  
- `netsh trace convert` コマンドでETLファイルをXMLファイルに変換する
- XMLファイルを解析して「Get-WindowsUpdateLog」コマンドを実行した際と同様の出力形式に整える

解析結果はTSV形式で `ParsedWindowsUpdate.log` というファイルに出力されます。

## 環境
Python 3.11以上

## インストール
```
$ pip install -r requirements.txt
```

## 使い方
Windows Updateのログファイル（.etl）が存在するフォルダを指定するだけです。  
基本、ログファイルは `C:\Windows\Logs\WindowsUpdate` に存在していると思います。

```
python win_update_log_parser.py C:\Windows\Logs\WindowsUpdate
```  
※直接 `C:\Windows\Logs\WindowsUpdate` を指定する際は**コマンドプロンプトを管理者として**実行してください。  

処理が正常に完了すると、以下のような出力が表示されます。

```
>python win_update_log_parser.py C:\Windows\Logs\WindowsUpdate
100%|██████████████████████████████████████████████████████████████████████████████████| 33/33 [00:08<00:00,  3.99it/s]
パース完了！
```

オプションを指定していない場合、解析結果はカレントディレクトリの `ParsedWindowsUpdate.log` というファイルに出力されます。

### オプション
- `-o`：出力先ディレクトリを指定可能です。
- `-h`：ヘルプを表示します。

## 解析結果の例
下図は生成された `ParsedWindowsUpdate.log` の例です。
![解析結果の例](/images/example.png)