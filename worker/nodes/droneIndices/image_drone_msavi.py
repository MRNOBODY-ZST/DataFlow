from . import _drone_base as B

INDEX_NAME = 'msavi'
CALC = B.calc_msavi
REQUIRED = ['NIR','Red']


class Operator:
    """计算无人机 msavi 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'msavi', B.calc_msavi, ['NIR','Red'], 'drone_msavi')
        return _impl(self, inputs, ctx)


ImageDroneMsaviNode = Operator
