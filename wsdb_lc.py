#!/usr/bin/env python

import numpy as np
import argparse
from astropy.time import Time
from wsdb import *




def cmdargs():
    parser = argparse.ArgumentParser(
        description="Grab a lightcurve from VIRAC v2 from the wsdb.")
    parser.add_argument("sourceid", type=int,
        help="Source ID")
    parser.add_argument("-p", "--plot", action="store_true",
        help="Display lightcurve figure")
    parser.add_argument("-i", "--saveimage", action="store_true",
        help="Save lightcurve figure to disk")
    parser.add_argument("-f", "--fold", type=float, default=0.0,
        help="Phase fold period (days default, or years with -y flag)")
    parser.add_argument("-y", "--years", action="store_true",
        help="Time axis in decimal years (default days)")
    parser.add_argument("-x", "--xscale", action="store_true",
        help="Scale the time axis to epochs with detections")
    parser.add_argument("-s", "--shiftx", action="store_true",
        help="Shift the time axis so the first detection is at t=0")
    return parser.parse_args()



# generate sql query
def gen_sql(sourceid, cols=None):
    if cols is None:
        cols = ["detid", "catid", "mjdobs", "mag", "emag", "x", "y",
                "dp_objtype", "dp_chi", "ext", "pxl_cnf", "sky"]
    colsql = ", ".join(["unnest({0}) as {0}".format(c) for c in cols])
    return "select %s from virac_lc where sourceid=%d" % (colsql, sourceid)



class LightCurve:
    def __init__(self, sourceid):
        # generate the sql query
        sql = gen_sql(sourceid)
        # execute the sql query
        # (i.e. grab the data from wsdb)
        lcdata = getsql(sql)
        # populate the class attributes
        self.sourceid = sourceid
        self.detid = lcdata["detid"]
        self.catid = lcdata["catid"]
        self.t = lcdata["mjdobs"]
        self.mag = lcdata["mag"]
        self.emag = lcdata["emag"]
        self.x = lcdata["x"]
        self.y = lcdata["y"]
        self.dp_objtype = lcdata["dp_objtype"]
        self.dp_chi = lcdata["dp_chi"]
        self.ext = lcdata["ext"]
        self.pxl_cnf = lcdata["pxl_cnf"]
        self.sky = lcdata["sky"]
        self.epoch_count = lcdata["mag"].size
        self.t_unit = "Julian days"


    def set_t_unit(self, t_unit):
        self.t_unit = t_unit


    def to_years(self):
        from astropy.time import Time
        _t = Time(self.t, format='mjd')
        self.t = _t.jyear
        self.set_t_unit("Julian years")






if __name__=="__main__":
    args = cmdargs()

    lc = LightCurve(args.sourceid)

    # convert from mjd to jyear if requested
    if args.years:
        lc.to_years()

    # if a plot is requested
    if args.plot or args.saveimage:

        # phase fold the data if requested
        if args.fold>0:
            lc.t = np.mod(lc.t, args.fold)
            xlabel = "t, phase folded (period %.3f) /  %s" % (args.fold,
                                                              lc.t_unit)
        elif args.shiftx:
            shift = np.min(lc.t[~np.isnan(lc.emags)])
            lc.t = lc.t - shift
            xlabel = "t - %.2f  /  %s" % (shift, lc.t_unit)
        else:
            xlabel = "t  /  %s" % lc.t_unit


        # import matplotlib
        if not args.plot:
            import matplotlib as mpl
            mpl.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12,3))
        plt.errorbar(lc.t, lc.mag, yerr=lc.emag,
                     fmt='.', markersize=3, linewidth=1, capsize=2)
        plt.xlabel(xlabel)
        plt.ylabel("K$_s$  /  mag")
        plt.gca().invert_yaxis()
        plt.grid()
        plt.tight_layout()

        if args.saveimage:
            plt.savefig("./Vv2_KsLC_{}.png".format(args.sourceid),
                        dpi=150, bbox_inches='tight')

        if args.plot:
            plt.show()
