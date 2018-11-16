# VReducer
[VRoidStudio](https://vroid.pixiv.net/)でエクスポートされたモデルを[Cluster](https://cluster.mu/)アバター用に軽量化する非公式スクリプトです。


## 動作環境
* python 2.7.x
* Windows10とWSL(Ubuntu)で動作確認済み

## 対応VRoidStudoバージョン
* 0.2.15
* 0.3.0

## 制限事項
* 現在対応してる髪マテリアルは1種類のみです
* ノーマルマップ、スフィアマップ、アウトラインは削除されます
* 現在のバージョンで対応している髪のマテリアル数は1つのみです
* 頂点の削減は非対応なので、頂点数を減らす場合はVRoidStudio上で調整をしてください。
* 非公式スクリプトのため、VRoidStudioのバージョンアップなどで使用不可能になる可能性があります。


## 準備
テクスチャ結合で[Pillow(PIL)](https://github.com/python-pillow/Pillow)ライブラリを使用しているため、以下のコマンドでPillowをインストールしてください。
```
$ pip install Pillow
```

## 使い方
```bash
$ python vreducer.py [VRM_FILE_PATH]
```
VRM_FILE_PATH：VRMファイルパス

変換後のファイルは以下のフォルダ以下に出力されます。
```
result
```

### 実行例
ファイルパス、変換前のモデル情報、変換後のモデル情報が表示されます。
```bash
$ python vreducer.py VRoid.vrm
VRoid.vrm
vrm materials: 16
materials: 16
textures: 29
images: 29
meshes 3
total primitives: 51
        primitives: 9
        primitives: 6
        primitives: 36
------------------------------
combining hair primitives...
shrinking materials...
combining materials...
cleaning...
------------------------------
vrm materials: 6
materials: 6
textures: 9
images: 9
meshes 3
total primitives: 16
        primitives: 9
        primitives: 6
        primitives: 1
```
上記例では以下のパスに変換後のファイルが出力されます。
```
result/Vroid.vrm
```

## 軽量化内容
### 髪プリミティブ結合
髪の毛のすべてのプリミティブとマテリアルを1つに結合します。
複数マテリアルを含む場合、先頭プリミティブのマテリアルに統一されます。

### マテリアル結合
#### 制服
| 結合マテリアル | 結合後のマテリアルパラメータ |
| -------------- | ------------------ | 
| 制服上下、リボン、靴 | 制服の上着 |
| 顔、体、白目、口 | 顔 |
| アイライン、まつ毛 | アイライン |
| 瞳孔、ハイライト | 瞳孔 |
| 髪の毛、頭皮の髪 | 髪の毛 |

##### テクスチャ縮小
| テクスチャ | 元サイズ | 変換後サイズ |
| ---------- | -------- | ------------ | 
| 体 | 2048x2048 | 1536x2048 |
| 制服の上着 | 2048x2048 | 2048x1536 |
| 顔 | 1024x1024 | 512x512 |
| 白目 | 1024x512 | 512x512 |
