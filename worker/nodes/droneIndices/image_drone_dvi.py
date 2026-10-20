from . import _drone_base as B

INDEX_NAME = 'dvi'
CALC = B.calc_dvi
REQUIRED = ['NIR','Red']


class Operator:
    """计算无人机 dvi 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'dvi', B.calc_dvi, ['NIR','Red'], 'drone_dvi')
        return _impl(self, inputs, ctx)


ImageDroneDviNode = Operator
