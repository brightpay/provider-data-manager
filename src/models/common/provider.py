class Provider:
    def __init__(self, name, specialty, hospital):
        self.name = name
        self.specialty = specialty
        self.hospital = hospital

    def __repr__(self):
        return f"<Provider(name={self.name}, specialty={self.specialty}, hospital={self.hospital})>"
