import os
import random
import time
from typing import List, Set, Tuple, overload

import mines

# try:
#     from typing import TYPE_CHECKING
# except:
#     TYPE_CHECKING = False

# if TYPE_CHECKING:
#     ...

directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
              [0, 1], [1, -1], [1, 0], [1, 1]]

# decided move, should be returned
MOVE_EXPLORE = 0
MARK_MINE = 1
MARK_SUSPICIOUS = 2  # maybe not used
MARK_REMOVE = 3  # maybe not used

# mark flag
GRID_MINE_SUSPICIOUS = -3  # maybe not used
GRID_UNKNOWN = -2
GRID_MINE_FLAG = -1

GRID_NO_MINE_NEARBY = 0  # special flag


class Marker(object):
    """
    表示一个标记。
    使用getStatus()获取标记，返回值为下列之一：
    非负整数：表示周围有多少雷。
    `GRID_MINE_FLAG`：此处被标记为雷区。
    `GRID_UNKNOWN`：此处未探索。
    `GRID_MINE_SUSPICIOUS`：此处被标记为可疑的。

    使用markmine()将此处标记为有雷的。
    使用markunknown()将此处标记去掉。
    使用marksuspicious()将此处标记为可疑（不推荐）。
    注意，如果被标记为非负整数了，则无法修改标记。
    标记为非负整数的过程不应该由算法完成，在explore阶段自动完成。
    """

    __slots__ = ["__mark"]

    def __init__(self) -> None:
        self.__mark = GRID_UNKNOWN

    def markmine(self) -> None:
        self.__checkup()
        self.__mark = GRID_MINE_FLAG

    def markunknown(self) -> None:
        self.__checkup()
        self.__mark = GRID_UNKNOWN

    def marksuspicious(self) -> None:
        self.__checkup()
        self.__mark = GRID_MINE_SUSPICIOUS

    def __checkup(self) -> None:
        if self.__mark >= 0:  # 说明已经探索且标记了
            raise AssertionError("算法错误")

    def marknum(self, num) -> None:
        if num < 0:
            raise ValueError("该值不可用该方法标记")
        self.__checkup()
        self.__mark = num

    def getStatus(self) -> int:
        """获取该格标记"""
        return self.__mark

    def isExplored(self) -> bool:
        """返回这格是否已经探索过."""
        return self.__mark >= 0


class MineSweepGame(object):
    def __init__(self) -> None:
        self.minemap = None  # 不要修改此对象
        self.markmap: List[List[Marker]] = []  # 记录玩家标记
        self.totalmine = 0  # constant in a game
        # 下面两项的和应等于totalmine
        self.leftmineNum = 0
        self.markedFlags = 0
        # 维护这个变量！
        self.edgeset = None

    def start(self, m: int, n: int, mineNum: int):
        self.restart(m, n, mineNum)

    def restart(self, m: int, n: int, mineNum: int):
        """重启游戏."""
        if mineNum > m*n-9:
            raise ValueError("地雷过多")
        self.totalmine = mineNum
        self.minemap = mines.MineMap(m, n)
        self.leftmineNum = mineNum
        self.markedFlags = 0
        self.markmap = [[Marker() for _ in range(n)] for _ in range(m)]
        self.edgeset: Set[Tuple[int, int]] = set()  # 将与未探索区域的边界点存储在这里

    @overload
    def explore(self, grid: Tuple[int, int]) -> int:
        ...

    @overload
    def explore(self, x: int, y: int) -> int:
        ...

    def explore(self, x: int, y: int = None) -> int:
        """
        Only explore here, and also mark explored grid.
        If return -1, the game should be over instantly.
        """
        # unpack parameter for overloaded case
        if type(x) is tuple:
            x, y = x

        # if this is the first time explore, generate the minemap
        if not self.minemap.mapinitialized:
            self.minemap.generate((x, y), self.leftmineNum)
        assert(y is not None)
        ans = self.minemap.explore(x, y)
        if ans != -1:
            self.markmap[x][y].marknum(ans)  # mark
        return ans

    def testValidCoordinate(self, x: int, y: int) -> bool:
        """测试输入的坐标是否在地图坐标格内."""
        return self.minemap.testValidCoordinate(x, y)

    def dfsExploreNoMineRegion(self, x: int, y: int) -> int:
        """assume that (x,y) is already marked as no mine nearby."""
        for pr in directions:
            xx = x+pr[0]
            yy = y+pr[1]
            if not self.testValidCoordinate(xx, yy):
                continue
            if self.markmap[xx][yy].isExplored():  # already marked
                continue
            self.explore(xx, yy)
            if self.markmap[xx][yy].getStatus() == GRID_NO_MINE_NEARBY:  # no mine, dfs it
                self.dfsExploreNoMineRegion(xx, yy)

    def randomStart(self):
        """start at random point."""
        x = random.randint(0, self.minemap.m-1)
        y = random.randint(0, self.minemap.n-1)
        answer = self.explore(x, y)

        if answer != 0:
            raise ValueError("断言错误，请修正初始化代码")

        self.dfsExploreNoMineRegion(x, y)

    def run(self):
        """Game Running."""
        if self.minemap.mapinitialized:
            raise RuntimeError("地图已经初始化了！")

        # 随机选择起点开始
        self.randomStart()

        # 计时
        time0 = time.time()

        while True:
            if self.checkwin():
                print("游戏结束")
                time1 = time.time()
                print(
                    f"地图行数{self.minemap.m}，列数{self.minemap.n}，地雷数{self.totalmine}，耗时{time1-time0}秒")
                return True

            if not self.gameloop():
                return False

    def checkwin(self):
        """Doing what you think it does."""
        if self.leftmineNum != 0:
            return False

        markmine = 0
        for row in self.markmap:
            for grid in row:
                status = grid.getStatus()
                if status == GRID_UNKNOWN or status == GRID_MINE_SUSPICIOUS:
                    return False
                if status == GRID_MINE_FLAG:
                    markmine += 1

        return markmine == self.totalmine

    def recheckNearby(self, x: int, y: int):
        """每步插旗、探索结束的时候，对周围情况重新处理并探索."""
        for pr in directions:
            xx = x+pr[0]
            yy = y+pr[1]
            if not self.testValidCoordinate(xx, yy):
                continue
            if self.markmap[xx][yy].getStatus() <= 0:  # only reheck known places
                continue

            if not self.dfsReheck(xx, yy):
                return False
        return True

    def dfsReheck(self, x: int, y: int):
        """use dfs to search all places that are sure."""
        totalmine = 0
        needexplore: Set[Tuple[int, int]] = set()
        for pr in directions:
            xx = x+pr[0]
            yy = y+pr[1]
            if not self.testValidCoordinate(xx, yy):
                continue

            status = self.markmap[xx][yy].getStatus()
            if status == GRID_MINE_FLAG:
                totalmine += 1
            elif status < 0:
                needexplore.add((xx, yy))

        if totalmine == self.markmap[x][y].getStatus():
            for xx, yy in needexplore:
                ans = self.explore(xx, yy)
                if ans == -1:
                    return False
            for xx, yy in needexplore:
                self.dfsReheck(xx, yy)
        return True

    def gameloop(self):
        """当该步失败时返回False，游戏结束"""
        self.scanEdge()

        x, y, move = self.decide()
        thismark = self.markmap[x][y]

        if move == MOVE_EXPLORE:
            ans = self.explore(x, y)
            if ans == -1:
                print("失败，游戏结束")
                return False
            if ans == 0:
                self.dfsExploreNoMineRegion(x, y)
        elif move == MARK_MINE:
            thismark.markmine()
            self.markedFlags += 1
            self.leftmineNum -= 1
            self.recheckNearby(x, y)
        elif move == MARK_SUSPICIOUS:
            thismark.marksuspicious()
        elif move == MARK_REMOVE:
            thismark.markunknown()
        return True

    def decide(self) -> Tuple[int, int, int]:
        """
        TODO.
        规范如下：
        返回一个三元组：
        (x, y, move)
        其中move是一个动作，仅有以下几类：
        * MOVE_EXPLORE，对(x,y)格探索
        * MARK_MINE，标记(x,y)格为地雷
        * MARK_SUSPICIOUS，不推荐，标记(x,y)格为可疑的
        * MARK_REMOVE，不推荐，去掉(x,y)的标记

        建议从self.edgemap入手。
        """

        # 注释掉下面两行以开始算法
        self.consolePlay()
        return self.getinputMove()

    def consolePlay(self):
        """Play in console."""
        os.system('clear')
        for i, row in enumerate(self.markmap):
            if i == 0:
                print(f"  ", end=' ')  # 两个空格，对齐
                for v, _ in enumerate(row):
                    print(v, end=' ')
                print(' ')
                print(''.join('-' for _ in range(self.minemap.n*2+2)))
            print(f"{i}:", end=' ')
            for mk in row:
                print(self.translateStatus(mk.getStatus()), end=' ')
            print(' ')

    @staticmethod
    def getinputMove() -> Tuple[int, int, int]:
        """Do what you think it is."""
        linestr = input("输入位置(x,y)以及移动方式，0代表探索，1表示插旗")
        ins = linestr.split()

        def _isint(s: str) -> bool:
            try:
                int(s)
            except Exception:
                return False
            return True

        def _check(s: List[str]) -> bool:
            return len(s) == 3 and s[2] in ['0', '1'] and all(_isint(x) for x in s[:2])

        while not _check(ins):
            print("输入无效。")
            linestr = input("输入位置(x,y)以及移动方式，0代表探索，1表示插旗\n")
            ins = linestr.split()

        return (int(ins[0]), int(ins[1]), int(ins[2]))

    @staticmethod
    def translateStatus(s: int) -> str:
        """Translate to human readable characters."""
        if s == GRID_UNKNOWN:
            return "."
        elif s == GRID_MINE_FLAG:
            return 'x'
        elif s == GRID_MINE_SUSPICIOUS:
            return '?'
        return str(s)

    def scanEdge(self):
        """Scan and add all elements into `self.edgeset`."""
        self.edgeset = set()
        for i, row in enumerate(self.markmap):
            for j, _ in enumerate(row):
                if self.__isEdge(i, j):
                    self.edgeset.add((i, j))

    def __isEdge(self, x: int, y: int) -> bool:
        if self.markmap[x][y].isExplored():
            return False
        for pr in directions:
            xx = x+pr[0]
            yy = y+pr[1]
            if not self.testValidCoordinate(xx, yy):
                continue
            if self.markmap[xx][yy].isExplored():
                return True
        return False
