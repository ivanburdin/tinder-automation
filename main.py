import argparse
import threading
import time

from Libs.Tinder.TinderHandler import TinderHandler
from Services.Notificator.NotificationService import NotificationService
from StatisticsLogger import log_statistics
from Utils.SettingsProvider import SettingsProvider

parser = argparse.ArgumentParser(description='Tinder data')

args = parser.parse_args()

START_STEP_DELAY_MS = 1000


def main():
    tinder = TinderHandler()

    # begin conversations
    begin_conversations = threading.Thread(target=tinder.begin_conversations)
    begin_conversations.start()
    time.sleep(START_STEP_DELAY_MS / 1000)
    # #
    # # handle conversations
    handle_conversations = threading.Thread(target=tinder.handle_conversations, args=())
    # #
    handle_conversations.start()
    time.sleep(START_STEP_DELAY_MS / 1000)
    # #
    # # # cleanup conversations
    # cleanup_matches = threading.Thread(target=tinder.cleanup_matches)
    # #
    # cleanup_matches.start()
    # time.sleep(START_STEP_DELAY_MS / 1000)

    # # swipes
    make_swipes = threading.Thread(target=tinder.make_swipes)

    make_swipes.start()
    time.sleep(START_STEP_DELAY_MS / 1000)
    #
    notification_service = threading.Thread(target=NotificationService.notification_service)
    notification_service.start()
    time.sleep(START_STEP_DELAY_MS / 1000)
    #
    # # statistics
    log_statistics_task = threading.Thread(target=log_statistics)

    log_statistics_task.start()

    # wait for all
    begin_conversations.join()
    handle_conversations.join()
    make_swipes.join()
    # cleanup_matches.join()
    notification_service.join()
    log_statistics_task.join()


if __name__ == "__main__":
    main()
