# import openai


class PairsClassifier():
    def __init__(self, pairs):
        self.pairs = pairs

    def classify(self):
        return self.pairs

    def dumb_result_to_file(self):
        pass

    def _ask_gpt_if_match(self, user1, user2):
        prompt = f"""
            User A:
            - Gender: {user1['gender']}
            - Interested in: {', '.join(user1['interested_in'])}
            - Age: {calculate_age(user1['birth_date'])}
            - Passions: {', '.join(user1['passion_names'])}

            User B:
            - Gender: {user2['gender']}
            - Interested in: {', '.join(user2['interested_in'])}
            - Age: {calculate_age(user2['birth_date'])}
            - Passions: {', '.join(user2['passion_names'])}

            Do you think these users would make a good match? Reply only 'Yes' or 'No'.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message['content'].strip().lower()
        return 1 if 'yes' in answer else 0

