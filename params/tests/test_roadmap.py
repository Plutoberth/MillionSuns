from ..roadmap import Roadmap, RoadmapParam


def test_roadmap_simple():
    # Just check that everything runs
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
        storage_min_energy_rate=RoadmapParam(start=0.2, end_min=0.05, end_max=0.1, step=0.05),
    )
