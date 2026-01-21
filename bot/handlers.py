from scheduler import PriceScheduler

scheduler_ref = None

def set_scheduler(scheduler):
    global scheduler_ref
    scheduler_ref = scheduler
