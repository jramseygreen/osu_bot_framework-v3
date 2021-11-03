import random

GAME_ATTR = {
    "head-to-head": 0,
    "tag-coop": 1,
    "team-vs": 2,
    "tag-team-vs": 3,
    "score": 0,
    "accuracy": 1,
    "combo": 2,
    "scorev2": 3,
    "HR": "HR",
    "DT": "DT",
    "FL": "FL",
    "HD": "HD",
    "FI": "FI",
    "FREEMOD": "FREEMOD",
    "osu": 0,
    "taiko": 1,
    "fruits": 2,
    "mania": 3,
    "any": random.randint(0, 3),
    "ranked": 1,
    "approved": 2,
    "qualified": 3,
    "loved": 4,
    "pending": 0,
    "wip": -1,
    "graveyard": -2

}