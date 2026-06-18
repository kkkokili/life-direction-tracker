import random
from utils.get_encouragement import get_random_quote

QUOTES=["Research in habit formation shows that consistency in the 60–80% range is often enough to build long-term behavior.\n You don’t need 100% perfection — staying around 70% is already strong progress.","Studies on habit formation suggest that sustainable change doesn’t require perfect execution. In fact, aiming for around 70% consistency is often more effective than chasing 100%, because it prevents burnout and all-or-nothing thinking.","You don’t need to be perfect. Behavioral research shows that staying consistent about 70% of the time is enough to build momentum. Long-term change is about trend, not perfection."]

def destructure_data():
    q, a = get_random_quote()
    return [q, a]

def get_random_feedback_quote():
    return random.choice(QUOTES)