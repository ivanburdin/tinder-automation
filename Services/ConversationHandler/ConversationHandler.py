from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Db.TinderDb import TinderDb
from Services.MessageProvider.MessageProvider import MessageProvider
from Services.Notificator.NotificationQueue import NotificationQueue


class ConversationHandler:

    @staticmethod
    def handle(tinder_client, match_id):

        if TinderDb.match_exists(match_id=match_id):
            return

        replicas_for_tinder = MessageProvider.messages_for_tinder()

        girl_responses, my_requests, whole_conversation = tinder_client.get_messages(match_id)
        match_id = whole_conversation[0]['match_id']

        replicas_sent_quantity = ConversationHandler._count_my_replicas_sent(whole_conversation, tinder_client)

        if replicas_sent_quantity == 0:
            tinder_client.send_message(match_id, replicas_for_tinder[0])
            StatisticsDb.increase_new_matches()  # i did not send anything but conversation exists, so she was first
            return

        my_last_replica_replied = ConversationHandler._replica_was_replied(whole_conversation,
                                                                           tinder_client,
                                                                           replicas_sent_quantity)

        if my_last_replica_replied or MessageProvider.should_send_notification():

            if replicas_sent_quantity >= MessageProvider.notification_threshold():

                if NotificationQueue.try_add(tinder_client, match_id, girl_responses, whole_conversation):

                    return

        if my_last_replica_replied and (replicas_sent_quantity + 1) <= len(replicas_for_tinder):
            '''replica indexes starts from 0 and if we already sent one replica,
                then we should send second replica, which index will be 1
                here we continue chat until get contact
                '''

            tinder_client.send_message(match_id, replicas_for_tinder[replicas_sent_quantity])

    @staticmethod
    def continue_chat(tinder_client, match_id):
        replicas_for_tinder = MessageProvider.messages_for_tinder()
        girl_responses, my_requests, whole_conversation = tinder_client.get_messages(match_id)
        replicas_sent_quantity = ConversationHandler._count_my_replicas_sent(whole_conversation, tinder_client)

        if (replicas_sent_quantity + 1) <= len(replicas_for_tinder):
            tinder_client.send_message(match_id, replicas_for_tinder[replicas_sent_quantity])

    @staticmethod
    def _replica_was_replied(whole_conversation, client, replied_counter):
        if replied_counter == 0:
            return False

        my_replica_replied_counter = 0

        for i, message in enumerate(whole_conversation):

            this_message_from_me = whole_conversation[i]['from'] == client.my_id
            last_message_from_me = (i >= 1) and whole_conversation[i - 1]['from'] == client.my_id

            if not this_message_from_me and last_message_from_me:
                my_replica_replied_counter += 1

            if my_replica_replied_counter == replied_counter:
                return True

        return False

    @staticmethod
    def _count_my_replicas_sent(whole_conversation, client):
        my_replicas_count = 0
        count_flag = True

        for i, message in enumerate(whole_conversation):

            message_from_me = True if whole_conversation[i]['from'] == client.my_id else False

            if count_flag and message_from_me:
                my_replicas_count += 1
                count_flag = False

            if not message_from_me:
                count_flag = True

        return my_replicas_count
