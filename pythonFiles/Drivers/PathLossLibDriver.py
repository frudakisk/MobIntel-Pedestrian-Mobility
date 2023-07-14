import sys
sys.path.append("pythonFiles")

from Functionality import PathLossLib as pll


print(pll.freeSpacePathLossLinear(10))
print(pll.freeSpacePathLossdB(10))
print(pll.FSPL(5))
print(pll.pathLossExponent(0.89))
print(pll.pathLossVanilla(10, 2.7, 30))