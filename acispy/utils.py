import Ska.Sun
import Ska.Numpy
import numpy as np
import logging
import sys
import os


acispyLogger = logging.getLogger("acispy")

ufstring = "%(name)-3s: [%(levelname)-9s] %(asctime)s %(message)s"
cfstring = "%(name)-3s: [%(levelname)-18s] %(asctime)s %(message)s"

acispy_sh = logging.StreamHandler(stream=sys.stderr)
# create formatter and add it to the handlers
formatter = logging.Formatter(ufstring)
acispy_sh.setFormatter(formatter)
# add the handler to the logger
acispyLogger.addHandler(acispy_sh)
acispyLogger.setLevel(20)
acispyLogger.propagate = False

mylog = acispyLogger


def ensure_tuple(obj):
    """
    This function ensures that *obj* is a tuple.  Typically used to convert
    scalar, list, or array arguments specified by a user in a context where
    we assume a tuple internally
    """
    if isinstance(obj, tuple):
        return obj
    elif isinstance(obj, (list, np.ndarray)):
        return tuple(obj)
    else:
        return obj,


def ensure_list(obj):
    """
    This function ensures that *obj* is a list.  Typically used to convert a
    string to a list, for instance ensuring the *fields* as an argument is a
    list.
    """
    if obj is None:
        return [obj]
    if not isinstance(obj, list):
        return [obj]
    return obj


def ensure_numpy_array(obj):
    """
    This function ensures that *obj* is a numpy array. Typically used to
    convert scalar, list or tuple argument passed to functions using Cython.
    """
    if isinstance(obj, np.ndarray):
        if obj.shape == ():
            return np.array([obj])
        # We cast to ndarray to catch ndarray subclasses
        return np.array(obj)
    elif isinstance(obj, (list, tuple)):
        return np.asarray(obj)
    else:
        return np.asarray([obj])


def calc_off_nom_rolls(states):
    times = np.array(0.5*(states['tstart'] + states['tstop']))
    atts = np.array([states[f"q{x}"] for x in range(1, 5)]).transpose()
    return np.array([Ska.Sun.off_nominal_roll(att, time)
                     for time, att in zip(times, atts)])


default_state_keys = ["ccd_count", "clocking", "ra", "dec", "dither", "fep_count",
                      "hetg", "letg", "obsid", "pcad_mode", "pitch", "power_cmd",
                      "roll", "si_mode", "simfa_pos", "simpos", "q1", "q2", "q3",
                      "q4", "trans_keys", "vid_board", "off_nom_roll", "hrc_15v"]

state_labels = {"ccd_count": "CCD Count",
                "clocking": "Clocking",
                "ra": "RA",
                "dec": "Dec",
                "dither": 'Dither',
                "fep_count": "FEP Count",
                "hetg": 'HETG',
                "letg": 'LETG',
                "obsid": "ObsID",
                "pcad_mode": "PCAD Mode",
                "pitch": "Pitch",
                "power_cmd": 'Power Command',
                "roll": "Roll",
                "si_mode": 'SI Mode',
                "simfa_pos": None,
                "simpos": "SIM-Z",
                "q1": "q1",
                "q2": "q2",
                "q3": "q3",
                "q4": "q4",
                "targ_q1": "target q1",
                "targ_q2": "target q2",
                "targ_q3": "target q3",
                "targ_q4": "target q4",
                "trans_keys": None,
                "vid_board": 'Video Board',
                "off_nom_roll": "Off-Nominal Roll",
                "tstart": "Start Time",
                "tstop": "Stop Time",
                "datestart": "Start Date",
                "datestop": "Stop Date",
                "date": "Date",
                "time": "Time",
                "hrc_15v": "HRC 15V",
                "hrc_24v": "HRC 24V",
                "hrc_i": "HRC-I",
                "hrc_s": "HRC-S",
                "dh_heater": "Detector Housing Heater",
                "eclipse": "Eclipse"}

mit_trans_table = {"BEP_PCB": "tmp_bep_pcb",
                   "BEP_OSC": "tmp_bep_osc",
                   "FEP0_MONG": "tmp_fep0_mong",
                   "FEP0_PCB": "tmp_fep0_pcb",
                   "FEP0_ACTEL": "tmp_fep0_actel",
                   "FEP0_RAM": "tmp_fep0_ram",
                   "FEP0_FB": "tmp_fep0_fb",
                   "FEP1_MONG": "tmp_fep1_mong",
                   "FEP1_PCB": "tmp_fep1_pcb",
                   "FEP1_ACTEL": "tmp_fep1_actel",
                   "FEP1_RAM": "tmp_fep1_ram",
                   "FEP1_FB": "tmp_fep1_fb",
                   "DEA28VDCA": "dea28volta",
                   "DEA24VDCA": "dea24volta",
                   "DEAM15VDCA": "deam15volta",
                   "DEAP15VDCA": "deap15volta",
                   "DEAM6VDCA": "deam6volta",
                   "DEAP6VDCA": "deap6volta",
                   "DEA28VDCB": "dea28voltb",
                   "DEA24VDCB": "dea24voltb",
                   "DEAM15VDCB": "deam15voltb",
                   "DEAP15VDCB": "deap15voltb",
                   "DEAM6VDCB": "deam6voltb",
                   "DEAP6VDCB": "deap6voltb"}

cti_simodes = ["TE_007AC", "TE_00B26", "TE_007AE",
               "TE_00CA8", "TE_00C60", "TN_000B4", 
               "TN_000B6", "TE_00C62"]


def get_display_name(ftype, name):
    if ftype.startswith("model"):
        display_name = name.upper() + " Model"
        if ftype != "model":
            display_name += str(ftype[-1])
    elif ftype == "states":
        display_name = state_labels[name]
    else:
        display_name = name.upper()
    return display_name


def bracket_times(times_in, times_out):
    ok = (times_out >= times_in[0]) & (times_out <= times_in[-1])
    return ok


def interpolate(times_in, times_out, data_in):
    data_out = Ska.Numpy.interpolate(data_in, times_in, times_out,
                                     method='linear', sorted=True)
    return data_out


def moving_average(a, n=5):
    return Ska.Numpy.smooth(a, window_len=n, window='flat')


def get_state_codes(msid):
    import Ska.tdb
    try:
        states = Ska.tdb.msids[msid].Tsc
    except:
        state_codes = None
    else:
        if states is None:
            state_codes = None
        else:
            states = np.sort(states.data, order='LOW_RAW_COUNT')
            state_codes = dict((state['STATE_CODE'], state['LOW_RAW_COUNT']) 
                               for state in states)
    return state_codes


def convert_state_code(ds, field):
    return np.array([ds.state_codes[field].get(val, -1) for val in ds[field]])


lr_root = "/data/acis/LoadReviews"


def find_load(load_name):
    load_week = load_name[:7]
    load_year = f"20{load_week[5:7]}"
    loaddir = os.path.join(lr_root, load_year, load_week)
    load_letter = sorted(os.listdir(loaddir))[-1][-1].upper()
    if len(load_name) == 7:
        load_name = load_week + load_letter
    return load_name


def plotdate2cxctime(dates):
    """
    Convert input CXC time (sec) to the time base required for the matplotlib
    plot_date function (days since start of year 1).

    :param times: iterable list of times
    :rtype: plot_date times
    """
    from cxotime import CxoTime
    # Find the cxctime of first time and use a relative offset from there
    cxctime0 = CxoTime(dates[0], format='plot_date').secs
    return (np.asarray(dates) - dates[0]) * 86400. + cxctime0


def dict_to_array(a):
    dtype = [(k, str(v.dtype)) for k, v in a.items()]
    data = np.zeros(a["datestart"].size, dtype=dtype)
    for k, v in a.items():
        data[k] = getattr(v, "value", v)
    return data
