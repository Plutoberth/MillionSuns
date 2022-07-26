from cProfile import run
from scenario_evaluator import run_scenarios
from params.roadmap import Scenario, Roadmap, RoadmapParam
from params.params import AllParams
import logging

def test_run_scenarios():
    r = Roadmap(
        start_year=2020,
        end_year=2050,
        solar_capacity_kw=RoadmapParam(
            start=4_000, end_min=50_000, end_max=150_000, step=20_000
        ),
        wind_capacity_kw=RoadmapParam(start=80, end_min=250, end_max=3_000, step=100),
        storage_capacity_kwh=RoadmapParam(start=0, end_min=50_000, end_max=400_000, step=50_000),
        storage_efficiency=RoadmapParam(
            start=85,
            end_min=90,
            end_max=95,
            step=5,
        ),
        storage_discharge=RoadmapParam(start=80, end_min=90, end_max=95, step=5),
    )

    scenario = next(r.scenarios)
    params = AllParams()
    res = run_scenarios.run_scenario(scenario, params)
