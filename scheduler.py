#This piece sends scheduled messages
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', seconds=30)
def timed_job():
    print('This job will run every thirty seconds.')

scheduler.start()