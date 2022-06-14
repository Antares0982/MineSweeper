import random
from typing import List, Tuple, overload

directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
              [0, 1], [1, -1], [1, 0], [1, 1]]


class MineBlock(object):
    def __init__(self, _type: bool = None) -> None:
        """If there is mine: type = true."""
        self.__setup = _type is not None
        self.__type = _type

    def setmine(self, mine: bool):
        if self.__setup:
            raise RuntimeError("该格已经设置完成")
        self.__type = mine

    def exploreBlock(self):
        """
        探索该格调用该方法。
        Return:
            True: 此处没有地雷
            False：此处有地雷，游戏应该终止。
        """
        if self.__type is None:
            raise RuntimeError("该格尚未初始化！")
        return not self.__type


class MineMap(object):
    # type declaration
    __map: List[List[MineBlock]]

    def __init__(self, m: int, n: int) -> None:
        """Init with m rows, n columns."""
        if m <= 5 or n <= 5:
            raise ValueError("地图过小")
        self.__private_param_init()
        self.__startup(m, n)

    def __startup(self, m: int, n: int):
        self.m = m
        self.n = n
        self.mapinitialized = False

    def __private_param_init(self):
        self.__m = None
        self.__n = None
        self.__map = None

    @property
    def m(self) -> int:
        return self.__m

    @m.setter
    def m(self, v: int) -> int:
        if self.__m is not None:
            raise RuntimeError("Should never set row number after initialize")
        if v <= 0:
            raise ValueError(f"Row number {v} is invalid")
        print("__m does not exist")
        self.__m = v

    @property
    def n(self) -> int:
        return self.__n

    @m.setter
    def n(self, v: int) -> int:
        if self.__n is not None:
            raise RuntimeError("Should never set col number after initialize")
        if v <= 0:
            raise ValueError(f"Column number {v} is invalid")
        self.__n = v

    @property
    def map(self) -> List[List[MineBlock]]:
        return self.__map

    def generate(self, startpoint: Tuple[int, int], mineNum: int):
        if self.mapinitialized:
            raise RuntimeError("地图已经初始化了")
        if mineNum <= 0 or self.m*self.n <= mineNum:
            raise ValueError("无效的地雷数")

        self.mapinitialized = True
        self.__map = [
            [MineBlock() for _ in range(self.n)]
            for _ in range(self.m)
        ]

        self.setRandomMines(startpoint, mineNum)

    def setRandomMines(self, startpoint: Tuple[int, int], mineNum: int):
        leftblock = self.m * self.n
        x, y = startpoint
        if (x == 0 or x == self.m-1) and (y == 0 or y == self.n-1):
            leftblock -= 4
        elif (x == 0 or x == self.m-1) or (y == 0 or y == self.n-1):
            leftblock -= 6
        else:
            leftblock -= 9

        if mineNum > leftblock:
            raise ValueError("地雷数太多")

        i = 0
        j = 0
        while mineNum != 0:
            if abs(i-x) <= 1 and abs(j-y) <= 1:
                self.map[i][j].setmine(False)
                leftblock += 1
            elif mineNum == leftblock:
                self.map[i][j].setmine(True)
                mineNum -= 1
            else:
                ismine = random.randint(1, leftblock) <= mineNum
                self.map[i][j].setmine(ismine)
                if ismine:
                    mineNum -= 1
            # update i, j and leftblock
            leftblock -= 1
            j = j+1 if j < self.n-1 else 0
            if j == 0:
                i += 1

        # setup the rest grids
        while i < self.m and j < self.n:
            self.map[i][j].setmine(False)
            j = j+1 if j < self.n-1 else 0
            if j == 0:
                i += 1

    def __cleanup(self):
        self.__private_param_init()

    def restart(self):
        if self.mapinitialized:
            raise RuntimeError("先停止游戏才可以重启")
        self.__cleanup()
        self.__startup()

    @overload
    def explore(self, grid: Tuple[int, int]) -> bool:
        ...

    @overload
    def explore(self, x: int, y: int) -> bool:
        ...

    def explore(self, arg1, arg2=None) -> int:
        """Explore this grid. If return -1, the game should be terminated immediately."""
        if type(arg1) is tuple:
            x, y = arg1  # first overload
        else:
            x, y = arg1, arg2  # second overload

        return self.__explore(x, y)

    def testValidCoordinate(self, x: int, y: int) -> bool:
        """该方法返回True时，(x,y)为有效的地图坐标."""
        return x >= 0 and y >= 0 and x < self.m and y < self.n

    def __explore(self, x: int, y: int) -> int:
        if type(x) is not int or type(y) is not int:
            raise ValueError("参数错误")
        if not self.testValidCoordinate(x, y):
            raise ValueError("无效的单元格")

        if not self.map[x][y].exploreBlock():  # boom!
            return -1

        minecount = 0  # count the nearby mines
        for p in directions:
            xx = x+p[0]
            yy = y+p[1]
            if not self.testValidCoordinate(xx, yy):
                continue
            if self.__testmine(xx, yy):
                minecount += 1

        return minecount

    def __testmine(self, x: int, y: int):
        """
        test if there is mine. 
        Should not stop game even exploreBlock() returned False, 
        since player cannot call this private method.
        """
        return not self.__map[x][y].exploreBlock()
