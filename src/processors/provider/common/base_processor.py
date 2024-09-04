import random
import string

class ProviderBaseProcessor:
    def process_data(self, data):
        raise NotImplementedError("Subclasses must implement this method")
    def _generate_provider_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9)),
