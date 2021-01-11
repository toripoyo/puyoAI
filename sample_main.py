import puyoField    # フィールド管理クラス
import puyoSystem   # システム管理クラス
import puyoAI       # AI管理クラス

import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':    
    AIClass = puyoAI.PuyoAI()
    systemClass = puyoSystem.PuyoSystem()
    fieldClass = puyoField.PuyoField()
    
    plt.ion()
    
    field = np.zeros((14, 6))
    for i in np.arange(36):
        field, field_evalution = AIClass.getNextField(field, systemClass.getTsumo())
        field, _, _ = fieldClass.getChainedField(field)
        
        print(i)
        print(np.flipud(field))
        print(field_evalution)
        
        img = fieldClass.getImage(field)
        plt.imshow(img)
        plt.pause(.01)