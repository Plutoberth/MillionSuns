from pydantic import BaseModel, Field, validator

from .base_dash_model import BaseDashModel


class Scenario(BaseModel):
    # clean energy sources
    solar_gen_kw: float
    wind_gen_kw: float

    # energy storage
    storage_cap_kwh: float
    storage_efficiency_p: float
    storage_discharge_p: float


class RoadmapParam(BaseDashModel):
    start: float = Field(..., title='Start Year Value', ge=0)
    end_min: float = Field(..., title='End Year Minimum Value', ge=0)
    end_max: float = Field(..., title='End Year Maximum Value', ge=0)
    step: float = Field(..., title='Step', ge=0)

    @validator('end_min')
    def v_end_min(cls, end_min: float, values: dict[str, float]):
        assert end_min >= values['start'], \
            'end_min must be greater or equal to start'
        return end_min

    @validator('end_max')
    def v_end_max(cls, end_max: float, values: dict[str, float]):
        assert end_max >= values['end_min'], \
            'end_max must be greater or equal to end_min'
        return end_max

    @validator('step')
    def v_step(cls, step: float, values: dict[str, float]):
        assert step <= (values['end_min'] - values['start']), \
            'step must be smaller or equal to end_min - start'
        return step


class Roadmap(BaseDashModel):
    start_year: int = Field(2020, title='Start Year', ge=0)
    end_year: int = Field(2050, title='End Year', ge=0)

    # clean energy sources
    solar_gen_kw: RoadmapParam = Field(..., title='Solar Generation Capacity (KW)')
    wind_gen_kw: RoadmapParam = Field(..., title='Wind Generation Capacity (KW)')

    # energy storage
    storage_cap_kwh: RoadmapParam = Field(..., title='Storage Capacity (KWH)')
    storage_efficiency_p: RoadmapParam = Field(
        ...,
        title='Storage Efficiency (% As fraction)',
        description='For every KWH entered, how mush is able to be drawn out.'
    )
    storage_discharge_p: RoadmapParam = Field(
        ...,
        title='Solar Discharge Depth (% As fraction)',
        description='How much of the battery\'s capacity can be drawn out at once.'
    )

    @validator('end_year')
    def v_end_max(cls, end_year: float, values: dict[str, int | RoadmapParam]):
        assert end_year >= values['start_year'], \
            'end_year must be greater or equal to start_year'
        return end_year

    @property
    def scenarios(self) -> list[Scenario]:
        # TODO
        return []
