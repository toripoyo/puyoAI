# ぷよぷよのフィールドを管理するクラス
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

class PuyoField():
# ---------------------------------------------------------------------- #
# 内部関数
    def __init__(self):
        # フィールド情報
        self.field_width = 6
        self.field_height = 14
        
        # フィールド画像生成用の変数
        self.__img_blank = Image.open("puyoImg/blank.png")
        self.__img_red = Image.open("puyoImg/red.png")
        self.__img_green = Image.open("puyoImg/green.png")
        self.__img_blue = Image.open("puyoImg/blue.png")
        self.__img_yellow = Image.open("puyoImg/yellow.png")
    
        self.__imgs = [self.__img_blank, self.__img_red, self.__img_green, self.__img_blue, self.__img_yellow]
        self.__color_type = [0,1,2,3,4]
    
        self.__img_width = 73     # ぷよ画像の横幅
        self.__img_height = 60    # ぷよ画像の縦幅
        
        self.__chain_bonus = [0,8,16,32,64,96,128,160,192,224,256,288,320,352,384,416,448,480,512]
        self.__same_erase_bonus = [0,2,3,4,5,6,7,10]
        self.__color_bonus = [0,3,6,12,24]
    
    # 指定マスのぷよの繋がっている個数を調べる
    def __checkConnectCount(self, field, field_mask, x_index, y_index, color, count):
        # フィールド範囲外だった場合は探索しない
        if x_index < 0 or y_index < 0:
            return 0
        if x_index >= self.field_width or y_index >= self.field_height:
            return 0
        # 調査対象の色と違った場合
        if field[y_index, x_index] != color:
            return 0
        # 空白マスだった場合
        if field[y_index, x_index] == 0:
            return 0
        # 調査済みだった場合
        if field_mask[y_index, x_index] != 0:
            return 0
        
        # チェック済みマーク
        field_mask[y_index, x_index] = 1
        
        # 該当する色だった場合
        count = 1
        if field[y_index, x_index] == color:
            count += self.__checkConnectCount(field, field_mask, x_index-1, y_index  , color, count)
            count += self.__checkConnectCount(field, field_mask, x_index+1, y_index  , color, count)
            count += self.__checkConnectCount(field, field_mask, x_index  , y_index-1, color, count)
            count += self.__checkConnectCount(field, field_mask, x_index  , y_index+1, color, count)
        return count

    # フィールド全体のぷよの繋がっている個数を調べる
    def __checkConnectCountAll(self, field):
        result_field = np.zeros((self.field_height, self.field_width))
        
        for x_index in np.arange(self.field_width):
            for y_index in np.arange(self.field_height):
                chain_test_color = field[y_index, x_index]                              # 連鎖を調べる色
                if chain_test_color > 0 or result_field[y_index, x_index] != 0:         # 空きマス、チェック済みマス以外だけ計算
                    field_check_mask = np.zeros((self.field_height, self.field_width))  # 連鎖チェック用マスク
                    result_field[y_index, x_index] = self.__checkConnectCount(field, field_check_mask, x_index, y_index, chain_test_color, 0)
                    result_field[np.where(field_check_mask != 0)] = result_field[y_index, x_index]
        
        return result_field
    
    # 繋がっているぷよを消す
    def __erasePuyo(self, field):
        field = field.copy()
        result_field = self.__checkConnectCountAll(field)
        field[np.where(result_field >= 4)] = 0
        return field, np.size(field[np.where(result_field >= 4)])
    
    # フィールドのぷよを落下させる
    def __dropPuyo(self, field):
        field = field.copy()
        for x_index in np.arange(self.field_width):
            tmp_field_col = field[:,x_index].copy()
            y_empty_cut = tmp_field_col[tmp_field_col > 0]
            zero_add_size = self.field_height - np.size(y_empty_cut)
            field[:,x_index] = np.hstack((y_empty_cut, np.zeros(zero_add_size)))
        return field

# ---------------------------------------------------------------------- #
# 外部公開関数
    # フィールドにぷよを落とす
    # Tsumoは縦2x横6のマスに配置
    def addNextPuyo(self, field, tsumo):
        field = field.copy()
        field = np.vstack((field, tsumo))
        for x_index in np.arange(self.field_width):
            tmp_field_col = field[:,x_index].copy()
            y_empty_cut = tmp_field_col[tmp_field_col > 0]
            zero_add_size = self.field_height+2 - np.size(y_empty_cut)
            field[:,x_index] = np.hstack((y_empty_cut, np.zeros(zero_add_size)))
        return field[:self.field_height,:]
    
    # ぷよを消した後のフィールドを求める
    def getChainedField(self, field):
        erase_count = 0
        chain_count = 0
        field = field.copy()

        field, erase_count = self.__erasePuyo(field)
        field = self.__dropPuyo(field)
        while(erase_count > 0):
            chain_count += 1
            field, erase_count = self.__erasePuyo(field)
            field = self.__dropPuyo(field)
            
        return field, chain_count
    
    # フィールドのぷよの高さを調べる
    def getFieldHeight(self, field):
        field = field.copy()
        invalid_place = False
        max_height = 0
        min_height = 99
        for x_index in np.arange(self.field_width):
            temp_line = field[:,x_index][field[:,x_index] > 0]
            now_line_height = np.size(temp_line)
            if now_line_height > max_height:
                max_height = now_line_height
            if now_line_height < min_height:
                min_height = now_line_height
            
            # 3,4列12段目に置いたらアウト
            if x_index == 2 or x_index == 3:
                if now_line_height >= 12:
                    invalid_place = True
            if now_line_height >= 13:
                invalid_place = True
                
        return max_height, min_height, invalid_place

    # フィールドのぷよの数を調べる
    def getPuyoNum(self, field):
        field = field.copy()
        field_puyo_only = field[np.where(field > 0)]
        return np.size(field_puyo_only)
    
    # フィールドのごみぷよの数を調べる
    
    # フィールドの副砲の連鎖数を調べる

    # フィールドの連鎖数と得点（★暫定★）を調べる
    def getChainScore(self, field):
        chain_count = 0
        chain_score = 0
        field = field.copy()
        
        field, erase_count = self.__erasePuyo(field)
        field = self.__dropPuyo(field) 
        while(erase_count > 0):
            chain_count += 1
            field, erase_count = self.__erasePuyo(field)
            field = self.__dropPuyo(field) 
                
            # 得点計算
            chain_bonus = self.__chain_bonus[np.clip(chain_count-1, 0, 18)]
            same_erase_bonus = self.__same_erase_bonus[np.clip(erase_count-4, 0, 7)]
            #color_bonus =
            
            chain_score += erase_count * (chain_bonus + same_erase_bonus) * 10
        
        if chain_count > 0 and chain_score == 0:
            chain_score = 10
            
        return chain_count, chain_score
    
    # フィールドを画像化する
    def getImage(self, field):
        field = field.copy()
        field_img = Image.new("RGB", (self.__img_blank.width  * self.field_width, 
                                      self.__img_blank.height * self.field_height))
        
        for y_index in np.arange(self.field_height):
            for x_index in np.arange(self.field_width):
                index_color = np.int(field[y_index, x_index])
                paste_image = self.__imgs[index_color].transpose(Image.ROTATE_180)
                field_img.paste(paste_image, (x_index* self.__img_width, y_index * self.__img_height))
        return field_img.transpose(Image.FLIP_TOP_BOTTOM)
    
    # 連鎖アニメを保存する
    def saveChainAnime(self, field):
        erase_count = 9999
        chain_count = -1
        imgs = []
        field = field.copy()
        
        while(erase_count > 0):
            imgs.append(self.getImage(field))
            field, erase_count = self.__erasePuyo(field)
            field = self.__dropPuyo(field)
            chain_count += 1
         
        imgs[0].save("result_" + str(chain_count) + ".gif",save_all=True, append_images=imgs[1:], optimize=False, duration=750, loop=0)


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
    
    tsumo = np.zeros((2, 6))
    tsumo[0,:] = [0,0,0,2,0,0]
    tsumo[1,:] = [0,0,0,4,0,0]
    
    fieldClass_test = PuyoField()
    field = fieldClass_test.addNextPuyo(field, tsumo)
    print("★getChainScore★")
    print(fieldClass_test.getChainScore(field))
    print("★getChainedField★")
    print(fieldClass_test.getChainedField(field))
    
    fieldClass_test.saveChainAnime(field)
    img = fieldClass_test.getImage(field)
    print("★getFieldHeight★")
    print(fieldClass_test.getFieldHeight(field))
    plt.imshow(img)
    
    # サンプルフィールド
    field = np.zeros((6, 14))
    field[:,1 ] = [2,0,1,0,0,0]
    field[:,0 ] = [2,2,2,1,1,1]
    field = field.T

    field = fieldClass_test.addNextPuyo(field, tsumo)
    print("★getChainScore★")
    print(fieldClass_test.getChainScore(field))
    print("★getChainedField★")
    print(fieldClass_test.getChainedField(field))
    
