import ska_helpers

__version__ = ska_helpers.get_version(__package__)

from acispy.dataset import EngArchiveData, \
    TracelogData, EngineeringTracelogData, \
    DEAHousekeepingTracelogData, \
    TenDayTracelogData, MaudeData, TelemData
from acispy.plots import DatePlot, MultiDatePlot, \
    PhaseScatterPlot, PhaseHistogramPlot, CustomDatePlot, \
    HistogramPlot, make_dateplots, DummyDatePlot
from acispy.thermal_models import SimulateECSRun, \
    ThermalModelRunner, ThermalModelFromLoad, \
    ThermalModelFromRun, SimulateSingleState
from acispy.load_review import ACISLoadReview


def test(*args, **kwargs):
    """
    Run py.test unit tests.
    """
    import testr
    return testr.test(*args, **kwargs)

