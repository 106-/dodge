dodge
===
強化学習の練習用ゲーム(避けゲー)

![動作画像](https://i.imgur.com/nZnalTv.gif)

## Requirements
DXライブラリをPythonから呼び出して描画しています. Windows用Python3.xが必要です.

↓ 必要なモジュールのインストール
```
> pip install keras tensorflow
```

## 使い方
- 行動価値観数をモデル化して学習
```
> python main.py model --sight_range 9
```
このモードのみ視界範囲の指定ができます.

- 学習したモデルを利用する
```
> python main.py saved_model --model_file over3000.h5
```

- QTableを使った学習
```
> python main.py table
```
メモリを500MBくらい使用するので注意が必要.

- 手動で操作する
```
> python main.py human
```

# 
DX Library Copyright (C) 2001-2019 Takumi Yamada.