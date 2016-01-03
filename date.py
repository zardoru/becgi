from datetime import datetime
from config import *

tp = lambda x: datetime.strptime(x, "%d/%m/%Y")
ssd = tp(START_SUBMIT_DATE)
esd = tp(END_SUBMIT_DATE)
sid = tp(START_IMPRESSION_DATE)
eid = tp(END_IMPRESSION_DATE)

# app vars (to be used etc)
def are_submissions_open():
    if not DEBUG:
        return ssd <= datetime.utcnow() <= esd
    else:
        return True

def are_impressions_open():
    if not DEBUG:
        return sid <= datetime.utcnow() <= sid
    else:
        return True

def can_see_submissions():
    if not DEBUG:
        return ssd <= datetime.utcnow()
    else:
        return True

def are_impressions_finished():
    if not DEBUG:
        return datetime.utcnow() >= eid
    else:
        return True
