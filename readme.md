# とこぷよを自動で置かせるやつ

30手で8連鎖くらいを作ってくれます。  
AIぷよの思考検討用にお使いください。

![puyo](result_10.gif)
# ファイルの説明

|ファイル名|説明|
|-|-|
|sample_main|連鎖を組ませるサンプルプログラム|
|puyoField|フィールド管理クラス。指定フィールドの連鎖数の計算など。|
|puyoSystem|ぷよのシステム管理クラス。ツモ生成など。|
|puyoAI|AIの思考ルーチン|

# 関数一覧
## puyoField

指定フィールドの連鎖得点の計算や、フィールドの各種操作（ツモを置くなど）を担当。

|関数名|機能|
|-|-|
|__checkConnectCount|指定したマスのぷよが何連結かを調べる|
|__checkConnectCountAll|フィールドの各マスが何連結かを調べる|
|__erasePuyo|4連結以上のぷよを消去する|
|__dropPuyo|フィールドで浮いているぷよを落下させる|
|addNextPuyo|フィールドにツモを置く（置く場所は2x6の配列で指定）|
|getChainedField|消せるぷよを消した後のフィールドを求める|
|getFieldHeight|フィールドのぷよの高さを調べる|
|getPuyoNum|フィールドのぷよの数を調べる|
|getChainScore|フィールドの連鎖数と得点を調べる|
|getImage|フィールド配列をぷよ画像にする|
|saveChainAnime|フィールドの連鎖アニメを保存する|

## puyoSystem

ぷよのシステムを担当。

|関数名|機能|
|-|-|
|getTsumo|ツモを引く。3x2の配列で、index0が操作ツモ、あとはNext1,2|

## puyoAI

ぷよのAIのサンプル。

|関数名|機能|
|-|-|
|__getPlaceableAllField|指定ツモで実現可能なフィールドをすべて求める|
|__getFieldChainable1|指定の1ツモで実現可能な最大得点を求める|
|__getFieldChainableZoro|ゾロ目を置いたときの最大得点を求める|
|getFieldEvalution|あるフィールドの評価関数を求める|
|getNextField|次に置く手を、評価関数をもとに決める|