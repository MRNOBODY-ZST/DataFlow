from . import _drone_base as B

INDEX_NAME = 'lci'
CALC = B.calc_lci
REQUIRED = ['NIR','RedEdge','Red']


class Operator:
    """计算无人机 lci 指数。"""

    def execute(self, inputs, ctx):
        _impl = B.make_execute_for_drone(
            'lci', B.calc_lci, ['NIR','RedEdge','Red'], 'drone_lci')
        return _impl(self, inputs, ctx)


ImageDroneLciNode = Operator
