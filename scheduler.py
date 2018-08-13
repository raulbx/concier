from apscheduler.schedulers.blocking import BlockingScheduler
import app

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=50)
def check_shopper_communicating_job():
    print('This job will run every 40 seconds.')
    app.check_active_conversations()

@scheduler.scheduled_job('interval', hours=24)
def get_all_coversations_active_more_than_24hours():
    print('This job will check all conversations active for more than 24 hours.')

@scheduler.scheduled_job('interval', minutes=15)
def check_if_shopper_still_interested():
    print('Check if shopper is still interested in talking to the expert')

scheduler.start()