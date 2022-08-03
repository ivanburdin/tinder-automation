class ConversationFormatter:
    @staticmethod
    def format(my_id, name, whole_conversation):
        output = ""
        for message in whole_conversation:

            if message['from'] == my_id:
                output += f'Me: {message["message"]}\n\n'
            else:
                output += f'{name}: {message["message"]}\n\n'

        return output
