from . import _drone_base as B

INDEX_NAME = 'savi'
CALC = B.calc_savi
REQUIRED = ['NIR','Red']


class Operator:
    """计算无人机 savi 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'savi', B.calc_savi, ['NIR','Red'], 'drone_savi')
        return _impl(self, inputs, ctx)


ImageDroneSaviNode = Operator
