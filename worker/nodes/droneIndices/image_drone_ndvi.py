from . import _drone_base as B

INDEX_NAME = 'ndvi'
CALC = B.calc_ndvi
REQUIRED = ['NIR','Red']


class Operator:
    """计算无人机 ndvi 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'ndvi', B.calc_ndvi, ['NIR','Red'], 'drone_ndvi')
        return _impl(self, inputs, ctx)


ImageDroneNdviNode = Operator
