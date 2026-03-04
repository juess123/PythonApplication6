
from collections import defaultdict

CLIP_STATS = {
    "count": defaultdict(int),
    "time": defaultdict(float),
}

def stat_inc(key, dt=0.0):
    CLIP_STATS["count"][key] += 1
    CLIP_STATS["time"][key] += dt