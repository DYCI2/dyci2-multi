# Parameters for Probabilistic Model
# WARNING : Files must exist in proba_model directory
model = dict(
    bigram = "bigram_save.xml",
    melody = "melody_chord_save.xml"
)

# Parameters for Oracle's Construction and Scenario
# WARNING : Files must exist in omnibook directory
oracle = dict (
    oracle      = "Another_Hairdo.xml",
    scenario    = "Another_Hairdo.xml"
)

# Parameters for Improvisation
improvisation = dict(
    length              = 200,
    continuity_factor   = 4,
    taboo_length        = 16,
    context_length      = 2
)
