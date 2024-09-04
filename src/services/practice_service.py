from src.models.common.practice import Practice

class PracticeService:
    @staticmethod
    def save_practice(practice_data):
        practice = Practice(
            name=practice_data['name'],
            specialty=practice_data['specialty'],
            hospital=practice_data['hospital']
        )
        # Save the practitioner to the database
        return practice
