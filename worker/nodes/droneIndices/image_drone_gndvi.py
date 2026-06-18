from . import _drone_base as B

INDEX_NAME = 'gndvi'
CALC = B.calc_gndvi
REQUIRED = ['NIR','Green']


class Operator:
    """计算无人机 gndvi 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'gndvi', B.calc_gndvi, ['NIR','Green'], 'drone_gndvi')
        return _impl(self, inputs, ctx)


ImageDroneGndviNode = Operator
