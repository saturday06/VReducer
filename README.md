# VReducer
[VRoidStudio](https://vroid.pixiv.net/)でエクスポートされたモデルを[Cluster](https://cluster.mu/)アバター用に軽量化する非公式スクリプトです。


## 動作環境
* python 2.7.x

## 対応VRoidStudoバージョン
* 0.2.15
* 0.3.0

## 注意点
* 髪の毛メッシュを結合してエクスポートしたモデルを使用してください。
* 頂点の削減は非対応なので、頂点数を減らしたい場合はVRoidStudio上で調整をお願いします。
* ノーマルマップ、スフィアマップは削除されます。
* マテリアル結合により基本色、影色が他のマテリアルに結合されるため、一部マテリアルの色が変わる可能性があります。

## v0.1.0更新点
* v0.1.0で複数の髪マテリアルに対応しました。

## 準備
テクスチャ結合で[Pillow(PIL)](https://github.com/python-pillow/Pillow)ライブラリを使用しているため、以下のコマンドでPillowをインストールしてください。
```
$ pip install Pillow
```

## 使い方
```bash
$ python vreducer.py [VRM_FILE_PATH] [-f|--force] [-h|--help] [-V|--version]
```


VRM_FILE_PATH: VRMファイルパス

-f, --force: このオプションが指定された場合ファイル保存時、確認なしに上書きする

-h, --help: ヘルプ表示

-V, --version: バージョン表示

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
combine hair primitives...
shrink materials...
combine materials...
clean...
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
saved.
```
上記例では以下のパスに変換後のファイルが出力されます。
```
result/Vroid.vrm
```

## 軽量化内容
### 髪プリミティブ結合
髪の毛のプリミティブをマテリアル毎に結合します。

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
テクスチャ結合時に以下のようにテクスチャが縮小されます

| テクスチャ | 元サイズ | 変換後サイズ |
| ---------- | -------- | ------------ | 
| 体 | 2048x2048 | 1536x2048 |
| 制服の上着 | 2048x2048 | 2048x1536 |
| 顔 | 1024x1024 | 512x512 |
| 白目 | 1024x512 | 512x512 |


## 制限事項
* 非公式スクリプトのため、VRoidStudioのバージョンアップなどで使用不可能になる可能性があります。
