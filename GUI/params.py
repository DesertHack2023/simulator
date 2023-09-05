from dataclasses import dataclass
from math import log


@dataclass
class Params:
    # Basic model related parameters
    POPULATION_SIZE = 2500
    POPULATION_DEMOGRAPHICS = [0.35, 0.8, 0.95, 1]
    SIMULATION_LENGTH = 180
    TIME_PER_FRAME = 0.2
    GRID_SIZE = 3
    CELL_SIZE = 1 / GRID_SIZE
    MAX_MOVEMENT = 0.05
    TRAVEL_RATE = 0.1
    COMORBIDITY_COEFFICIENTS = [0.7, 0.9, 1.1, 1.3]
    RANDOM_SEED = 0
    GRID_PROBABILITIES = [
        0.1312769922816259,
        0.1390833168942316,
        0.3045853365542704,
        0.4356598378729931,
        0.5622315487782497,
        0.661694550602876,
        0.7233137507793976,
        0.9097747150485921,
        1.0,
    ]
    TRAVEL_PROBABILITES = [
        [
            [
                0.0,
                0.10929820017699199,
                0.27276162832436446,
                0.3757530039414913,
                0.4070611554404322,
                0.5141784494471481,
                0.6862885066982833,
                0.8897540885298117,
                1.0,
            ],
            [
                0.01276555432675935,
                0.01276555432675935,
                0.2549058943340527,
                0.3165936951304174,
                0.3313424092336104,
                0.5261744388243516,
                0.605427611942261,
                0.8333672107397323,
                1.0,
            ],
            [
                0.15892428359862334,
                0.25671979924004384,
                0.25671979924004384,
                0.4112738227241321,
                0.4689758058768651,
                0.5133234764625129,
                0.6529014952735729,
                0.9486386571496084,
                1.0,
            ],
        ],
        [
            [
                0.10971379925019822,
                0.2878653035220132,
                0.32803681379718236,
                0.32803681379718236,
                0.41482954573864717,
                0.5309870905775683,
                0.6608006095631672,
                0.75172681155559,
                1.0,
            ],
            [
                0.009644405249296112,
                0.2094320374511056,
                0.4376333030633881,
                0.45569664963375833,
                0.45569664963375833,
                0.7076895066463159,
                0.8330073254559883,
                0.901153496212128,
                1.0,
            ],
            [
                0.06026892867591995,
                0.19565788907547954,
                0.32939093982734113,
                0.5182163362815277,
                0.6682045420575002,
                0.6682045420575002,
                0.8840014633111152,
                0.9638518606813694,
                1.0,
            ],
        ],
        [
            [
                0.08414150309199522,
                0.18637911894866807,
                0.24348125544191232,
                0.4330323728765049,
                0.5914437868519774,
                0.7308537039886345,
                0.7308537039886345,
                0.8950430045152277,
                1.0,
            ],
            [
                0.19785810173842416,
                0.2650401869246098,
                0.319379404747021,
                0.4786510388002174,
                0.6844413299933607,
                0.7661163638941053,
                0.8477272086754665,
                0.8477272086754665,
                1.0,
            ],
            [
                0.2126451818934487,
                0.26513495503947604,
                0.3493490329508198,
                0.6236939408914254,
                0.6542097654894706,
                0.688875326780259,
                0.7852000076475122,
                1.0,
                1.0,
            ],
        ],
    ]

    # Contact radius
    # The contact radius is a function of the population density
    # CONTACT_RADIUS = 3 / POPULATION_DENSITY
    CONTACT_RADIUS = 3 / POPULATION_SIZE
    CONTACT_RADIUS_SQUARED = CONTACT_RADIUS**2

    # State transition related parameters
    INITIAL_INFECTED = 2
    INFECTION_RATE = 0.2
    HOSPITALIZATION_RATE = 0.5
    MORTALITY_RATE = 0.2 * HOSPITALIZATION_RATE
    MORTALITY_COEFFICIENT = 2
    INCUBATION_PERIOD = 5
    INFECTION_PERIOD = 10
    IMMUNITY_PERIOD = 30

    # Metrics related parameters
    DOUBLING_TIME_WINDOW_LENGTH = 3
    LOG_2 = log(2)
    PLOT_EFFECTIVE_REPRODUCTIVE_NUMBER = False

    # Intervention related parameters
    RULE_COMPLIANCE_RATE = 0.9

    # Hospital related paramters
    HOSPITAL_CAPACITY = 0.06
    HOSPITALIZATION_COST = 5000
    HOSPITAL_ENABLED = False

    # Vaccination related parameters
    VACCINATION_ENABLED = False
    VACCINATION_START = 60
    VACCINATION_RATE = 0.01
    VACCINATION_COST = 1000
    INITIAL_VACCINATED = 0

    # Lockdown related parameters
    LOCKDOWN_ENABLED = False
    LOCKDOWN_COST = 500
    LOCKDOWN_DAYS = []
    LOCAL_LOCKDOWN = False
    LOCKDOWN_STRATEGY = "block"

    # Lockdown strategy related parameters
    LOCKDOWN_LEVEL = 0.5
    LOCKDOWN_START = 50
    LOCKDOWN_STOP = 100
    ALT_LOCKDOWN_FRAMES_ON = 20
    ALT_LOCKDOWN_FRAMES_OFF = 10
    DAY_LOCKDOWN = [True, True, True, True, True, False, False]

    # Hygiene related parameters
    HYGIENE_ENABLED = False
    HYGIENE_RATE = 0.6
    HYGIENE_COST = 100

    # Travel restrictions related parameters
    TRAVEL_RESTRICTIONS_ENABLED = False
    TRAVEL_RESTRICTIONS_COST = 200
