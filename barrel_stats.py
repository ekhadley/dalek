import numpy as np
from tqdm import trange

# bonus program!! Threw this together for the steam barrel acheivement. It just tells you how many points you are likely to score
# in barrel game in a certain number of kicks, with a certain probability of sinking each barrel. barrel game rules explained below.
# short answer: to get the acheivement (3000 pts in 100 kicks), you need about .8 successful kick rate to do it in 100 kicks exactly
# if we want some leeway, and try to do it in 90 kicks, we need ~.835 sink rate.

# a 'cycle' ends and starts every second time the hoop hits the left wall. if the hoop hits the left wall twice without the
# player sinking a barrel, we have 'missed' the cycle. The speed of a hoop can only change when it hits the left wall,
# not the right, and it can change speed mid cycle (1st bounce).
# we kick once per cycle. a missed kick resets the phase to 1. a successful kick increments the phase by 1. max phase is 4
# normal barrels award 10 points per kick. Every 5th barrel is red, and wards 25 base points.
# the score of a successul kick is 10*phase for normal barrels, and 25*phase for red barrels.

# happy kicking!

def trial(nkicks, pwin):
    phase, score, streak, streaks = 1, 0, 0, []
    for k in range(nkicks):
        if (k+1) % 5 == 0: pts = 25*phase
        else: pts = 10*phase
        if np.random.rand() < pwin:
            phase = min(phase+1, 4)
            score += pts
            streak += 1
            #print(f'kick {k+1}: success! phase {phase}, score {score}, streak {streak}')
        else:
            streaks.append(streak)
            phase, streak = 1, 0
            #print(f'kick {k+1}: fail! phase {phase}, score {score}, streak {streak}')
    astreak = sum(streaks)/len(streaks) if len(streaks) > 0 else nkicks
    return score, astreak

def expected(nkicks, pwin, trials):
    scores, streaks = [], []
    for i in trange(trials):
        score, streak = trial(nkicks, pwin)
        scores.append(score)
        streaks.append(streak)
    ascore = sum(scores)/len(scores)
    astreak = sum(streaks)/len(streaks)
    return ascore, astreak

print(expected(100, .796, 50000))
print(expected(90, .834, 50000))