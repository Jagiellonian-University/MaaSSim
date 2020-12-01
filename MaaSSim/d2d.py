from .driver import driverEvent
import pandas as pd
import numpy as np
from dotmap import DotMap
import math
import random

def D2D_veh_exp(*args,**kwargs):
    #calculate vehicle KPIs (global and individual)
    params = kwargs.get('params',None)
    simrun = kwargs.get('simrun',None)
    vehindex = kwargs.get('vehindex',None)
    df = simrun['rides'].copy() #results of previous simulation
    DECIDES_NOT_TO_DRIVE = df[df.event == driverEvent.DECIDES_NOT_TO_DRIVE.name].veh # track drivers out
    dfs = df.shift(-1) # to map time periods between events
    dfs.columns = [_+"_s" for _ in df.columns] #columns with _s are shifted
    df = pd.concat([df,dfs],axis=1) # now we have time periods
    df = df[df.veh == df.veh_s] #filter for the same vehicles only
    df=df[~(df.t == df.t_s)] # filter for positive time periods only
    df['dt'] = df.t_s - df.t # make time intervals
    ret = df.groupby(['veh','event'])['dt'].sum().unstack() #aggregated by vehicle and event
    del ret.columns.name
    ret = ret.reindex(vehindex) #update for vehicles with no record
    ret['nRIDES'] = df[df.event == driverEvent.ARRIVES_AT_DROPOFF.name].groupby(
        ['veh']).size().reindex(ret.index)
    ret['nREJECTED'] = df[df.event == driverEvent.IS_REJECTED_BY_TRAVELLER.name].groupby(
        ['veh']).size().reindex(ret.index)
    for status in driverEvent:
        if status.name not in ret.columns:
            ret[status.name]=0 #cover all statuss
    DECIDES_NOT_TO_DRIVE.index = DECIDES_NOT_TO_DRIVE.values
    ret['OUT'] = DECIDES_NOT_TO_DRIVE
    ret['OUT'] = ~ret['OUT'].isnull()
    ret['DRIVING_TIME'] = ret.REJECTS_REQUEST + ret.IS_REJECTED_BY_TRAVELLER + ret.IS_ACCEPTED_BY_TRAVELLER + ret.DEPARTS_FROM_PICKUP + ret.CONTINUES_SHIFT
    ret['DRIVING_DIST'] = ret['DRIVING_TIME'] * (params.speeds.ride/1000)
    ret['REVENUE'] = (ret.DEPARTS_FROM_PICKUP * (params.speeds.ride/1000) * params.fares.km).add(params.fares.base * ret.nRIDES) * (1-params.fares.commission)
    ret['COST'] = ret['DRIVING_DIST'] * (params.drivers.fuel)
    ret['NET_INCOME'] = ret['REVENUE'] - ret['COST']
    ret = ret[['nRIDES','nREJECTED', 'DRIVING_TIME', 'DRIVING_DIST', 'REVENUE', 'COST', 'NET_INCOME', 'OUT']+[_.name for _ in driverEvent]].fillna(0) #nans become 0
    ret.index.name = 'veh'

    #KPIs
    kpi = ret.agg(['sum','mean','std'])
    kpi['nV']=ret.shape[0]
    return {'veh_exp':ret,'veh_kpi':kpi}

def D2D_driver_out(*args, **kwargs):
    """ returns True if driver decides not to drive, and False if he drives"""
    veh = kwargs.get('veh',None)

    perc_income = veh.veh.expected_income
    if ~veh.veh.registered:
        return True
    elif veh.sim.params.probabilistic:
        util_d = veh.sim.params.drivers.particip.beta * perc_income
        util_nd = veh.sim.params.drivers.particip.beta * veh.veh.res_wage
        prob_d_reg = math.exp(util_d) / (math.exp(util_d) + math.exp(util_nd))
        prob_d_all = prob_d_reg

        if prob_d_all < random.random():
            #print('I go out because I expect to earn too litle today')
            return True
        else:
            return False
    else:
        if perc_income < veh.veh.res_wage:
            #print('I go out because I expect to earn too litle today')
            return True
        else:
            return False

def update_d2d_exp(*args, **kwargs):
    "updating drivers' day experience (incl determination of new perceived income)"
    sim = kwargs.get('sim',None)
    params = kwargs.get('params',None)
    run_id = len(sim.res)-1
#     ret = dict()
    hist = pd.concat([~sim.res[_]['veh_exp'].OUT for _ in range(0,run_id+1)],axis=1,ignore_index=True)
    worked_days = hist.sum(axis=1)

    ret = pd.DataFrame()
    ret['veh'] = np.arange(1,params.nV+1)
    ret['informed'] = sim.vehicles.informed.to_numpy()
    ret['registered'] = sim.vehicles.registered.to_numpy()
    ret['out'] = sim.res[run_id].veh_exp.OUT.to_numpy()
    ret['init_perc_inc'] = sim.vehicles.expected_income.to_numpy()
    ret['exp_inc'] = sim.res[run_id].veh_exp.NET_INCOME.to_numpy()
    ret.loc[ret.out == True, 'exp_inc'] = np.nan
    ret['worked_days'] = worked_days.to_numpy()
    experienced_driver = (ret.worked_days >= params.drivers.omega).astype(int)
    kappa = (experienced_driver / params.drivers.omega + (1 - experienced_driver) / (ret.worked_days + 1)) * (1 - ret.out)
    new_perc_inc = (1 - kappa) * ret.init_perc_inc + kappa * ret.exp_inc
    ret['new_perc_inc'] = new_perc_inc.to_numpy()
    ret.loc[(ret.registered == True) & (ret.out == True), 'new_perc_inc'] = ret.loc[(ret.registered == True) & (ret.out == True), 'init_perc_inc']
    ret = ret.set_index('veh')

    return  ret

def D2D_stop_crit(*args, **kwargs):
    "returns True if simulation will be stopped, False otherwise"
    res = kwargs.get('d2d_res', None)
    params = kwargs.get('params', None)

    if len(res) < params.min_it:
        return False
    else:
        ret = (res[len(res)-1].new_perc_inc - res[len(res)-1].init_perc_inc) / res[len(res)-1].init_perc_inc
        if ret.abs().max() <= params.conv:
            return True
        else:
            return False

def platform_regist(inData, end_day, **kwargs):
    "determine probability of registering at platform overnight for all unregistered drivers"
    params = kwargs.get('params', None)
    exp_reg_drivers = end_day.loc[end_day['registered'] == True]
    average_perc_income = exp_reg_drivers.new_perc_inc.mean()

    samp = np.random.rand(params.nV) <= params.drivers.regist.samp   # Sample of drivers making registration choice

    util_reg = params.drivers.regist.beta * average_perc_income
    util_not_reg = params.drivers.regist.beta * (inData.vehicles.res_wage + params.drivers.regist.cost_comp)
    prob_regist = np.exp(util_reg) / (np.exp(util_reg) + np.exp(util_not_reg))
    regist_decision = (np.random.rand(params.nV) < prob_regist) & inData.vehicles.informed & samp

    prev_regist = inData.vehicles.registered.to_numpy()
    registered = (np.concatenate(([prev_regist],[regist_decision]),axis=0).transpose()).any(axis=1)
    regist_res = pd.DataFrame(data = {'registered': registered, 'expected_income': end_day.new_perc_inc})
    regist_res.loc[((inData.vehicles.registered == False) & (regist_res.registered == True)), "expected_income"] = average_perc_income

    return regist_res

def word_of_mouth(inData, **kwargs):
    "determine which drivers are informed before the start of the new day"
    params = kwargs.get('params', None)
    nV_inf = inData.vehicles.informed.sum()
    nV_uninf = params.nV - nV_inf
    if nV_uninf > 0:
        exp_inf_day = (params.drivers.inform.beta * nV_inf * nV_uninf) / params.nV
        prob_inf = exp_inf_day / nV_uninf
    else:
        prob_inf = 0

    new_inf = np.random.rand(params.nV) < prob_inf
    prev_inf = inData.vehicles.informed.to_numpy()
    informed = (np.concatenate(([prev_inf],[new_inf]),axis=0).transpose()).any(axis=1)
    res_inf = pd.DataFrame(data = {'informed': informed}, index=np.arange(1,params.nV+1))

    return res_inf

def D2D_summary(d2d):
    "create day-to-day stats"
    inform = pd.concat([d2d[i].informed for i in range(len(d2d))],axis=1)
    inform.columns = list(range(len(d2d)))
    regist = pd.concat([d2d[i].registered for i in range(len(d2d))],axis=1)
    regist.columns = list(range(len(d2d)))
    ptcp = pd.concat([~d2d[i].out for i in range(0,len(d2d))],axis=1)
    ptcp.columns = list(range(len(d2d)))
    init_perc_inc = pd.concat([d2d[i].init_perc_inc for i in range(len(d2d))],axis=1)
    init_perc_inc.columns = list(range(len(d2d)))
    exp_inc = pd.concat([d2d[i].exp_inc for i in range(len(d2d))],axis=1)
    exp_inc.columns = list(range(len(d2d)))
    evol_micro = DotMap()
    evol_micro.inform = inform
    evol_micro.regist = regist
    evol_micro.ptcp = ptcp
    evol_micro.perc_inc = init_perc_inc
    evol_micro.exp_inc = exp_inc
    evol_stats = pd.DataFrame({'inform': evol_micro.inform.sum(), 'regist': evol_micro.regist.sum(), 'particip': evol_micro.ptcp.sum(), 'mean_perc_inc': evol_micro.perc_inc.mean(), 'mean_exp_inc': evol_micro.exp_inc.mean()})
    evol_stats.index.name = 'day'

    return evol_micro, evol_stats

def generate_vehicles_d2d(_inData, _params=None):
    """
    generates vehicle database
    index is consecutive number if dataframe
    registered whether drivers have already made sign up decision
    position is random graph node
    event is set to STARTS_DAY
    """

    vehs = generate_vehicles(_inData, _params.nV)

    # vehs = list()
    # for i in range(_params.nV + 1):
    #     vehs.append(empty_series(inData_.vehicles, id=i))
    #
    # vehs = pd.concat(vehs, axis=1, keys=range(1, _params.nV + 1)).T
    # vehs.event = driverEvent.STARTS_DAY
    vehs.expected_income = float("NaN")
    vehs['res_wage'] = np.random.normal(_params.drivers.res_wage.mean, _params.drivers.res_wage.std, _params.nV)
    vehs['informed'] = (np.random.rand(_params.nV) < _params.drivers.inform.prob_start)
    vehs['registered'] = (np.random.rand(_params.nV) < _params.drivers.regist.prob_start) & vehs.informed
    vehs.loc[vehs.registered == True, "expected_income"] = _params.drivers.init_income
    # vehs.platform = 0
    # vehs.shift_start = 0
    # vehs.shift_end = 60 * 60 * 24
    # vehs.pos = vehs.pos.apply(lambda x: int(rand_node(inData_.nodes)))

    return vehs
