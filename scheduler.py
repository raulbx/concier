from apscheduler.schedulers.blocking import BlockingScheduler
import app

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=50)
def check_shopper_communicating_job():
    print('This job will run every 40 seconds.')
    app.check_active_conversations()

scheduler.start()