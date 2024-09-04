from src.models.common.practitioner import Practitioner

class PractitionerService:
    @staticmethod
    def save_practitioner(practitioner_data):
        practitioner = Practitioner(
            name=practitioner_data['name'],
            specialty=practitioner_data['specialty'],
            hospital=practitioner_data['hospital']
        )
        # Save the practitioner to the database
        return practitioner
