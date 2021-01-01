# ぷよぷよのシステムを管理するクラス
import numpy as np
import random

class PuyoSystem():

# ---------------------------------------------------------------------- #
# 外部公開関数
    def __init__(self):
        self.__tsumo_depth = 3
        self.tsumo = np.zeros((self.__tsumo_depth, 2))
        
        for i in np.arange(self.__tsumo_depth):
            self.tsumo[i,:] = np.array([random.randint(1,4), random.randint(1,4)])
        
    def getTsumo(self):
        self.tsumo = self.tsumo[1:,:] 
        self.tsumo = np.vstack((self.tsumo, np.array([random.randint(1,4), random.randint(1,4)])))
        return self.tsumo

# ---------------------------------------------------------------------- #
# 単体テストプログラム
if __name__ == '__main__':    
    system_test = PuyoSystem()
    a = system_test.getTsumo()
    print(system_test.getTsumo())
    print(system_test.getTsumo())
    print(system_test.getTsumo())