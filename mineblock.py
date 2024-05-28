import random
from enum import Enum

# 設置遊戲參數
BLOCK_WIDTH = 30    # 方塊的寬度
BLOCK_HEIGHT = 16   # 方塊的高度
SIZE = 20           # 方塊大小
MINE_COUNT = 99     # 地雷數量

# 方塊狀態的枚舉類別
class BlockStatus(Enum):
    normal = 1  # 未點擊
    opened = 2  # 已點擊
    mine = 3    # 地雷
    flag = 4    # 標記為地雷
    ask = 5     # 標記為問號
    bomb = 6    # 踩中地雷
    hint = 7    # 被雙擊的周圍
    double = 8  # 正被鼠標左右鍵雙擊

# 地雷類別
class Mine:
    def __init__(self, x, y, value=0):
        self._x = x
        self._y = y
        self._value = 0
        self._around_mine_count = -1
        self._status = BlockStatus.normal
        self.set_value(value)

    def __repr__(self):
        return str(self._value)
        # return f'({self._x},{self._y})={self._value}, status={self.status}'

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x

    x = property(fget=get_x, fset=set_x)

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y

    y = property(fget=get_y, fset=set_y)

    def get_value(self):
        return self._value

    def set_value(self, value):
        if value:
            self._value = 1
        else:
            self._value = 0

    value = property(fget=get_value, fset=set_value, doc='0:非地雷 1:雷')

    def get_around_mine_count(self):
        return self._around_mine_count

    def set_around_mine_count(self, around_mine_count):
        self._around_mine_count = around_mine_count

    around_mine_count = property(fget=get_around_mine_count, fset=set_around_mine_count, doc='四周地雷數量')

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    status = property(fget=get_status, fset=set_status, doc='BlockStatus')

# 地雷方塊類別
class MineBlock:
    def __init__(self):
        self._block = [[Mine(i, j) for i in range(BLOCK_WIDTH)] for j in range(BLOCK_HEIGHT)]

        # 隨機埋雷
        for i in random.sample(range(BLOCK_WIDTH * BLOCK_HEIGHT), MINE_COUNT):
            self._block[i // BLOCK_WIDTH][i % BLOCK_WIDTH].value = 1

    def get_block(self):
        return self._block

    block = property(fget=get_block)

    def getmine(self, x, y):
        return self._block[y][x]

    def open_mine(self, x, y):
        # 踩到雷了
        if self._block[y][x].value:
            self._block[y][x].status = BlockStatus.bomb
            return False

        # 先把狀態改為 opened
        self._block[y][x].status = BlockStatus.opened

        around = _get_around(x, y)

        _sum = 0
        for i, j in around:
            if self._block[j][i].value:
                _sum += 1
        self._block[y][x].around_mine_count = _sum

        # 如果周圍沒有雷，那麼將周圍8個未中未點開的遞歸算一遍
        # 這就能實現一點出現一大片打開的效果了
        if _sum == 0:
            for i, j in around:
                if self._block[j][i].around_mine_count == -1:
                    self.open_mine(i, j)

        return True

    def double_mouse_button_down(self, x, y):
        if self._block[y][x].around_mine_count == 0:
            return True

        self._block[y][x].status = BlockStatus.double

        around = _get_around(x, y)

        sumflag = 0     # 周圍被標記的雷數量
        for i, j in _get_around(x, y):
            if self._block[j][i].status == BlockStatus.flag:
                sumflag += 1
        # 周邊的雷已經全部被標記
        result = True
        if sumflag == self._block[y][x].around_mine_count:
            for i, j in around:
                if self._block[j][i].status == BlockStatus.normal:
                    if not self.open_mine(i, j):
                        result = False
        else:
            for i, j in around:
                if self._block[j][i].status == BlockStatus.normal:
                    self._block[j][i].status = BlockStatus.hint
        return result

    def double_mouse_button_up(self, x, y):
        self._block[y][x].status = BlockStatus.opened
        for i, j in _get_around(x, y):
            if self._block[j][i].status == BlockStatus.hint:
                self._block[j][i].status = BlockStatus.normal

# 獲取周圍方塊的座標
def _get_around(x, y):
    """返回(x, y)周圍的點的坐標"""
    # 這裡注意，range 末尾是開區間，所以要加 1
    return [(i, j) for i in range(max(0, x - 1), min(BLOCK_WIDTH - 1, x + 1) + 1)
            for j in range(max(0, y - 1), min(BLOCK_HEIGHT - 1, y + 1) + 1) if i != x or j != y]

