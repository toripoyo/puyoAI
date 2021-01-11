# ぷよぷよのAIクラス
import numpy as np
import puyoField    # フィールド管理クラス
from concurrent.futures import ProcessPoolExecutor

class PuyoAI():
    def __init__(self):
        self.__fieldClass = puyoField.PuyoField()
        self.__place_pattern = 22   # あるツモを置けるパターン
        
        # ★アニメ保存用
        self.__max_chain = 0

# ---------------------------------------------------------------------- #
# 内部関数
    # 指定のツモで実現可能なフィールドを全て求める
    def __getPlaceableAllField(self, field, tsumo):       
        # ツモを置ける全ての組み合わせを列挙
        tsumo_field = np.zeros((2, self.__fieldClass.field_width, self.__place_pattern))
        cnt = 0
        # 縦置き順方向（6通り）
        for i in np.arange(self.__fieldClass.field_width):
            tsumo_field[0,i,cnt] = tsumo[0]
            tsumo_field[1,i,cnt] = tsumo[1]
            cnt += 1
        # 縦置き逆方向（6通り）
        for i in np.arange(self.__fieldClass.field_width):
            tsumo_field[0,i,cnt] = tsumo[1]
            tsumo_field[1,i,cnt] = tsumo[0]
            cnt += 1 
        # 横置き右方向（5通り）
        for i in np.arange(self.__fieldClass.field_width-1):
            tsumo_field[0,i,cnt] = tsumo[0]
            tsumo_field[0,i+1,cnt] = tsumo[1]
            cnt += 1 
        # 横置き左方向（5通り）
        for i in np.arange(self.__fieldClass.field_width-1):
            tsumo_field[0,i,cnt] = tsumo[1]
            tsumo_field[0,i+1,cnt] = tsumo[0]
            cnt += 1  

        # ツモパターン全てに対して、フィールドを計算
        next_field = np.zeros((self.__fieldClass.field_height, self.__fieldClass.field_width, self.__place_pattern))
        for i in np.arange(self.__place_pattern):
            # 指定ツモを置いた時の仮のフィールド
            next_field[:,:,i] = self.__fieldClass.addNextPuyo(field, tsumo_field[:,:,i])

        return next_field

    # 指定の1ツモで実現可能な最大連鎖得点を求める
    def __getFieldChainable1(self, field, tsumo1):
        tsumo1_field = self.__getPlaceableAllField(field, tsumo1)
        
        # 指定1ツモで実現可能な連鎖数の配列（22通り）を求める
        next_field_score = np.zeros(self.__place_pattern)
        for i in np.arange(self.__place_pattern):
            next_field_score[i] = self.__fieldClass.getChainScore(tsumo1_field[:,:,i])[1]
        
        return np.max(next_field_score), np.average(next_field_score)

    # フィールドにゾロ目を置いた時の最大連鎖得点を求める
    def __getFieldChainableZoro(self, field):
        max_chain = np.zeros(4)
        for i in np.arange(4):
            max_chain[i] = self.__getFieldChainable1(field, np.array([i,i]))[0]
            
        return np.max(max_chain)
       

# ---------------------------------------------------------------------- #
# 外部公開関数
    # フィールドの評価関数を求める
    def getFieldEvalution(self, field, tsumo_all):
        field = field.copy()
        tsumo1 = tsumo_all[1,:]
        tsumo2 = tsumo_all[2,:]
        field_evalution = 0
 

        # 谷ペナルティ
        field_max_height, field_min_height, invalid_place = self.__fieldClass.getFieldHeight(field)
        tani = field_max_height - field_min_height
        if tani >= 4:
            field_evalution -= tani * 10


        # 3,4列12段目、13段目に置く置き方はペナルティ
        if invalid_place == True:
            field_evalution -= 999999
            return field_evalution # 早期Returnで速度アップ


        # ぷよを消してしまう置き方をしない
        now_chain_num = self.__fieldClass.getChainScore(field)[0]     # 現在の連鎖数
        # ぷよを消してしまう置き方の場合
        if now_chain_num != 0:
            # 連鎖アニメを保存する
            if self.__max_chain < now_chain_num and now_chain_num > 5:
                self.__max_chain = now_chain_num
                self.__fieldClass.saveChainAnime(field)
            field_evalution -= 999999
            return field_evalution # 早期Returnで速度アップ

        # 2ツモまでのフィールドの評価値を求める        
        next_field_score1 = np.zeros(self.__place_pattern)                              # 1ツモ目で実現可能な得点
        next_field_score2 = np.zeros((self.__place_pattern, self.__place_pattern))      # 2ツモ目で実現可能な得点
        next_field_score_zoro = self.__getFieldChainableZoro(field)                     # ゾロ目で実現可能な得点
        next_field_score_zoro -= self.__fieldClass.getChainedField(field)[2] * 50       # 消した後の残りぷよ個数
        #next_field_score_zoro += np.sum(self.__fieldClass.checkConnectCountAll(field))  # 連結数


        # 1ツモ目の全フィールドの組み合わせを取得
        tsumo1_field = self.__getPlaceableAllField(field, tsumo1)
        for i in np.arange(self.__place_pattern):
            # 1ツモ目で実現可能な得点
            next_field_score1[i] = self.__fieldClass.getChainScore(tsumo1_field[:,:,i])[1]          # 連鎖得点
            next_field_score1[i] -= self.__fieldClass.getChainedField(tsumo1_field[:,:,i])[2] * 50  # 消した後の残りぷよ個数
            #next_field_score1[i] += np.sum(self.__fieldClass.checkConnectCountAll(tsumo1_field[:,:,i])) # 連結数
            
            # 2ツモ目の全フィールドの組み合わせを取得（1ツモ目で消さない場合のみ）
            if next_field_score1[i] <= 0:
                tsumo2_field = self.__getPlaceableAllField(tsumo1_field[:,:,i], tsumo2)
                for j in np.arange(self.__place_pattern):
                    next_field_score2[i, j] = self.__fieldClass.getChainScore(tsumo2_field[:,:,j])[1]          # 連鎖得点
                    next_field_score2[i, j] -= self.__fieldClass.getChainedField(tsumo2_field[:,:,i])[2] * 50  # 消した後の残りぷよ個数
                    #next_field_score2[i, j] += np.sum(self.__fieldClass.checkConnectCountAll(tsumo2_field[:,:,i])) # 連結数
       
        # フィールド評価値の計算
        field_evalution += np.max((np.max(next_field_score2), np.max(next_field_score1), next_field_score_zoro)) # 連鎖得点の最大値
        
        return field_evalution
    
    # マルチスレッド用ラッパ
    def getFieldEvalutionMulti(self, args):
        field, tsumo_all = args[0], args[1]
        return self.getFieldEvalution(field, tsumo_all)
    
    # 次に置く手を決める
    def getNextField(self, field, tsumo_all):
        # 操作ツモで実現可能なフィールドの組み合わせをすべて求める
        field_evalution = np.zeros(self.__place_pattern)
        tsumo_now_field = self.__getPlaceableAllField(field, tsumo_all[0,:])
        
        # 操作ツモので実現可能なフィールドの評価値を全て求め、ベストなフィールド（＝どこに置くか？）を選択する
        # マルチスレッド処理
        multi_thread = True
        if multi_thread:
            args = []
            for i in np.arange(self.__place_pattern):
                args.append([tsumo_now_field[:,:,i], tsumo_all])
            with ProcessPoolExecutor(8) as e:
                result = e.map(self.getFieldEvalutionMulti, args)
            field_evalution = [r for r in result]
        else:
        # シングルスレッド処理（内容は同じ）
            for i in np.arange(self.__place_pattern):
                field_evalution[i] = self.getFieldEvalution(tsumo_now_field[:,:,i], tsumo_all)
        
        best_index = np.argmax(field_evalution)
        best_field = tsumo_now_field[:,:,best_index]
        
        return best_field, field_evalution[best_index]
    
# ---------------------------------------------------------------------- #
# 単体テストプログラム
if __name__ == '__main__':    
    # サンプルフィールド
    field = np.zeros((6, 14))
    field[:,13] = [0,0,0,0,1,0]
    field[:,12] = [0,0,4,0,4,3]
    field[:,11] = [0,3,4,0,1,1]
    field[:,10] = [1,2,2,3,3,1]
    field[:,9 ] = [3,2,4,1,3,4]
    field[:,8 ] = [3,1,1,4,1,1]
    field[:,7 ] = [3,1,4,1,3,4]
    field[:,6 ] = [2,3,4,2,4,4]
    field[:,5 ] = [4,2,2,3,3,1]
    field[:,4 ] = [3,3,3,2,3,1]
    field[:,3 ] = [4,4,4,1,1,4]
    field[:,2 ] = [2,1,2,3,3,4]
    field[:,1 ] = [2,2,1,2,2,3]
    field[:,0 ] = [1,1,2,3,4,4]
    field = field.T
    
    tsumo = np.zeros((3, 2))
    
    puyoAI_test = PuyoAI()
    print(puyoAI_test.getFieldEvalution(field, tsumo))