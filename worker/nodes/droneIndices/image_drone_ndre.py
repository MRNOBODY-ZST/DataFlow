from . import _drone_base as B

INDEX_NAME = 'ndre'
CALC = B.calc_ndre
REQUIRED = ['NIR','RedEdge']


class Operator:
    """计算无人机 ndre 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'ndre', B.calc_ndre, ['NIR','RedEdge'], 'drone_ndre')
        return _impl(self, inputs, ctx)


ImageDroneNdreNode = Operator
