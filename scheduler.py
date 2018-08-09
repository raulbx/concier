from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', seconds=30)
def timed_job():
    print('This job will run every thirty seconds.')

scheduler.start()