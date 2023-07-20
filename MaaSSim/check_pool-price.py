################################################################################
# Module: pool_price.py
# Making choices betweenpooled and single rides in MaaSSim
# uses (ExMAS) 
# Rafal Kucharski @ Jagiellonian University
################################################################################
import numpy as np
import os
import json
import pandas as pd

def pool_price_fun(sim, veh, request, sp):
    kpi_type = sim.params.kpi
    print(sp.operating_cost)

    # Added
    # function used inside the f_match to update the choice of the driver (pool/single)

    logger = sim.logger.critical  # set what do you want to see from the logger

    if len(request.rides) > 0:  # only if there is a choice
        logger('this is request {} with {} available rides.'.format(request.pax_id, request.rides))
        available_rides = sim.inData.sblts.rides.loc[request.rides]  # this is set in shared.py
        still_available_rides = list()
        for ride_index, ride in available_rides.iterrows():
            if all([sim.pax[_].pax.event.value <= 1 for _ in ride.indexes]):
                still_available_rides.append(ride_index)  # see all the travellers of this pooled ride are still available
                logger("ride {} available {}".format(ride.name, [sim.pax[_].pax.event.value for _ in ride.indexes]))
            else:
                logger("ride {} not available {}".format(ride.name, [sim.pax[_].pax.event.value for _ in ride.indexes]))
        logger('this is request {} with {} still available rides.'.format(request.pax_id, still_available_rides))

        if len(still_available_rides) > 0:  # only if we still have a choice

            still_available_rides = sim.inData.sblts.rides.loc[still_available_rides]

            #### HERE COMES YOUR CHOICE FUNCTIONS
            # This is a random function.

            still_available_rides['pickup_dist'] = still_available_rides.apply(lambda row: sim.inData.skim[veh.veh.pos][row.nodes[1]], axis=1)  # distance from driver initial position to the first pickup point
            still_available_rides['trav_dist'] = still_available_rides['dist'] + still_available_rides['pickup_dist']  # distance from driver's initial position to the drop off point of the last passenger

            still_available_rides["operating_cost"] = still_available_rides["trav_dist"].apply(lambda x: x * sp.operating_cost)
            still_available_rides["profit"] = still_available_rides["driver_revenue"] - still_available_rides["operating_cost"]

            if sp.get('probabilistic', False):
                mu = sp.get('choice_mu', 0.3)
                still_available_rides['u'] = np.exp(mu * still_available_rides.profit)
                total_u = still_available_rides['u'].sum()
                still_available_rides['probability'] = still_available_rides['u'] / total_u

                my_choice = still_available_rides.sample(1, weights='probability')
            else:
                # select by max profit
                if kpi_type == 1:
                    my_choice = still_available_rides[still_available_rides["profit"] == still_available_rides["profit"].max()].squeeze()
                    # print(my_choice)
                    # ride = my_choice
                    ride = still_available_rides[still_available_rides["profit"] == still_available_rides["profit"].max()]

                # select by max profit on solo rides !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                elif kpi_type == 2:
                    # Filter the available rides with only solo rides (rides with a single index value)
                    rf_solo = still_available_rides[still_available_rides['indexes_orig'].map(len) == 1]

                    if not rf_solo.empty and 1 in rf_solo['indexes_orig'].iloc[0]:
                        # If there is a solo ride with index 1, pick it as my_choice
                        my_choice = rf_solo[rf_solo['indexes_orig'] == [1]].iloc[0]
                    else:
                        # If no solo ride with index 1 is available, set my_choice to None or handle it accordingly
                        my_choice = None  # or any other appropriate handling for the case when no solo ride is available

                # select by max profit on pooled rides !!!!!!!!!!!!!!!!!!!!!!!!!
                elif kpi_type == 3:
                    print("hell")
                    # rf = still_available_rides[(still_available_rides['indexes_orig'].map(len) > 1)]
                    rf = still_available_rides[(still_available_rides['indexes_orig'].map(len) > 1)]
                    my_choice = rf[rf['profit'] == rf['profit'].max()].iloc[0]
                    ride = rf[rf['profit'] == rf['profit'].max()]

                    veh.rdf = pd.concat([veh.rdf, ride])

            logger('vehicle {} has {} choices'.format(veh.id, len(still_available_rides)))

           
            for pax in my_choice.indexes:
                sim.inData.requests.loc[pax].sim_schedule = my_choice.sim_schedule
                # maybe here we need to update the position and leader of the schedule - and set that the schedule got triggered? - so far no bugs

    return request, sim