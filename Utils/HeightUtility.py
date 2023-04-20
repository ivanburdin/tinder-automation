import re

from Utils.SettingsProvider import SettingsProvider


class HeightUtility:

    @staticmethod
    def fits(user):
        user_height = HeightUtility.get_height(user)

        if user_height:
            return user_height > int(SettingsProvider.get_settings()['min_height_cm'])

        return True

    @staticmethod
    def get_height(user):
        user_height = None

        bio = user['user']['bio']

        heights_from_bio = [x for x in re.findall(r'[0-9]{3}', bio, flags=re.IGNORECASE) if 140 < int(x) < 201]
        if heights_from_bio:
            user_height = int(heights_from_bio[0])

        height_data = [d for d in user['user'].get('selected_descriptors', []) if d.get('section_name', '') == 'Height']

        if height_data:
            h_value = height_data[0]['measurable_selection']['value']
            h_units = height_data[0]['measurable_selection']['unit_of_measure']

            if h_units == 'cm':
                user_height = int(h_value)
            else:
                pass

        return user_height


