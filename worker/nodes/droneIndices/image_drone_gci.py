from . import _drone_base as B

INDEX_NAME = 'gci'
CALC = B.calc_gci
REQUIRED = ['NIR','Green']


class Operator:
    """计算无人机 gci 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'gci', B.calc_gci, ['NIR','Green'], 'drone_gci')
        return _impl(self, inputs, ctx)


ImageDroneGciNode = Operator
