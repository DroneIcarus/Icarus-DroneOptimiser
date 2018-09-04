#If you ever want to try it in command line:
#python3 main.py "test.plan" "testGenerated"

import sys, os
import logging
import logging.config
import json
from MissionPlanner import MissionPlanner
from MissionPlanner import MissionPlan


#main function
if __name__ == "__main__":

    path = 'logging.json'

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    #logger.warn('warn message')
    logger.error('error message')
    #logger.critical('critical message')

    if len(sys.argv) <= 1:
        sys.exit("ERROR: main.py is missing arguments in Route Optimizer script.")

    logger.info("Starting the mission planner...")
    plan = MissionPlan.MissionPlan(sys.argv[1])

    logger.debug("points %s", plan.get_mission().get_waypoints())
    mp = MissionPlanner.MissionPlanner(plan, "nameTest")
    # mp.getMissionPointGraph()
    # mp.getMissionPointOrder()
    mp.run()

    # Once we have all the intermediates waypoints we can rewrite the mission
    plan.write_to_file(sys.argv[2])
