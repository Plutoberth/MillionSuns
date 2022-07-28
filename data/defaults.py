defaults = {
  "general": {
    "coal_must_run": [  # values change due to decommissioning of plants.
      # TODO: add comment which plant decommissioning accounts for each line
      {"start_year": 2020, "end_year": 2020, "interpo":  {"type": "constant", "value": 2440.0}},
      {"start_year": 2021, "end_year": 2021, "interpo":  {"type": "constant", "value": 2380.0}},
      {"start_year": 2022, "end_year": 2022, "interpo":  {"type": "constant", "value": 1620.0}},
      {"start_year": 2023, "end_year": 2023, "interpo":  {"type": "constant", "value": 1500.0}},
      {"start_year": 2024, "end_year": 2039, "interpo":  {"type": "constant", "value": 1440.0}},
      {"start_year": 2040, "end_year": 2044, "interpo":  {"type": "constant", "value": 960.0}},
      {"start_year": 2045, "end_year": 2048, "interpo":  {"type": "constant", "value": 480.0}},
      {"start_year": 2049, "end_year": 2050, "interpo":  {"type": "constant", "value": 0.0}}
    ]
  },
  "costs": {
    "solar": {  # PV-Average. TODO: add detailed prices and distribution per PV type as params
      "capex": [
        {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 3912, "end_value": 3274}},
        {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 3274, "end_value": 2669}},
        {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 2669, "end_value": 2368}},
        {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 2368, "end_value": 2503}},
        {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 2503, "end_value": 2312}},
        {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 2312, "end_value": 2166}}
      ],
      "opex": [
        {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 62, "end_value": 55}},
        {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 55, "end_value": 46}},
        {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 46, "end_value": 41}},
        {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 41, "end_value": 40}},
        {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 40, "end_value": 37}},
        {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 37, "end_value": 34}}
      ],
      "lifetime": [
        {"start_year": 2020, "end_year": 2050, "interpo": {"type": "constant", "value": 25}}
      ]
    },
    "wind": {
      "capex": [
        {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 4600, "end_value": 4240}},
        {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 4240, "end_value": 4000}},
        {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 4000, "end_value": 3860}},
        {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 3860, "end_value": 3760}},
        {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 3760, "end_value": 3660}},
        {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 3600, "end_value": 3600}}
      ],
      "opex": [
        {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 92, "end_value": 84}},
        {"start_year": 2025, "end_year": 2040, "interpo": {"type": "linear", "start_value": 84, "end_value": 72}},
        {"start_year": 2040, "end_year": 2050, "interpo": {"type": "constant", "value": 72}}
      ],
      "lifetime": [
        {"start_year": 2020, "end_year": 2050, "interpo": {"type": "constant", "value": 25}}
      ]
    },
    "storage": {
      "capex": [
        {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 1004.0, "end_value": 652.6}},
        {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 652.6, "end_value": 471.9}},
        {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 471.9, "end_value": 371.5}},
        {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 371.5, "end_value": 321.3}},
        {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 321.3, "end_value": 281.1}},
        {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 281.1, "end_value": 261.0}}
      ],
      "opex": [
        {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 15.6, "end_value": 12.8}},
        {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 12.8, "end_value": 10.8}},
        {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 10.8, "end_value": 9.6}},
        {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 9.6, "end_value": 8.8}},
        {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 8.8, "end_value": 8.4}},
        {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 8.4, "end_value": 8}}
      ],
      "lifetime": [
        {"start_year": 2020, "end_year": 2029, "interpo": {"type": "constant", "value": 15}},
        {"start_year": 2030, "end_year": 2050, "interpo": {"type": "constant", "value": 20}}
      ]
    },
    "gas": {  # CCGT
      "capex": [
        {"start_year": 2020, "end_year": 2050, "interpo": {"type": "constant", "value": 3785}}
      ],
      "opex": [
        {"start_year": 2020, "end_year": 2050, "interpo": {"type": "constant", "value": 164}}
      ],
      "variable_opex": [  # var opex + fuel
        {"start_year": 2020, "end_year": 2050, "interpo": {"type": "constant", "value": 0.0139 + 0.1176}}
      ],
      "lifetime": [
        {"start_year": 2020, "end_year": 2050, "interpo": {"type": "constant", "value": 35}}
      ]
    }
  },
  "emissions": {
    "gas": {
      # TODO: use the YoY change as parameters instead of the prices
      "CO2": 397,
      "SOx": 0,
      "NOx": 0.16,
      "PMx": 0.02

    },
    "coal": {}
  },
  "emissions_costs": {
    "CO2": [
      {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 167, "end_value": 185}},
      {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 185, "end_value": 1206}},
      {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 206, "end_value": 226}},
      {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 226, "end_value": 248}},
      {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 248, "end_value": 269}},
      {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 269, "end_value": 291}}
    ],
    "SOx": [
      {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 85381, "end_value": 100868}},
      {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 100868, "end_value": 119164}},
      {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 119164, "end_value": 139086}},
      {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 139086, "end_value": 162337}},
      {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 162337, "end_value": 189476}},
      {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 189476, "end_value": 221151}}
    ],
    "NOx": [
      {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 118208, "end_value": 139650}},
      {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 139650, "end_value": 164980}},
      {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 164980, "end_value": 192561}},
      {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 192561, "end_value": 224752}},
      {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 224752, "end_value": 262325}},
      {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 262325, "end_value": 306179}}
    ],
    "PMx": [
      {"start_year": 2020, "end_year": 2025, "interpo": {"type": "linear", "start_value": 270760, "end_value": 319873}},
      {"start_year": 2025, "end_year": 2030, "interpo": {"type": "linear", "start_value": 319873, "end_value": 377894}},
      {"start_year": 2030, "end_year": 2035, "interpo": {"type": "linear", "start_value": 377894, "end_value": 441068}},
      {"start_year": 2035, "end_year": 2040, "interpo": {"type": "linear", "start_value": 441068, "end_value": 514803}},
      {"start_year": 2040, "end_year": 2045, "interpo": {"type": "linear", "start_value": 514803, "end_value": 600865}},
      {"start_year": 2045, "end_year": 2050, "interpo": {"type": "linear", "start_value": 600865, "end_value": 701314}}
    ]
  }
}
