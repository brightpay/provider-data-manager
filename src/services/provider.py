from src.models.common.provider import Provider

class ProviderService:
    @staticmethod
    def save_provider(practitioner_data):
        provider = Provider(
            name=provider_data['name'],
            specialty=provider_data['specialty'],
            hospital=provider_data['hospital']
        )
        # Save the practitioner to the database
        return provider_data
