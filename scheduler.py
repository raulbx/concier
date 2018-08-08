#This piece sends scheduled messages
from apscheduler.schedulers.background import BackgroundScheduler

#scheduler = BackgroundScheduler()

#@scheduler.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job will run every three minutes.')

#scheduler.start()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(timed_job, 'interval', seconds=30)
    scheduler.start()