class Practitioner:
    def __init__(self, name, specialty, hospital):
        self.name = name
        self.specialty = specialty
        self.hospital = hospital

    def __repr__(self):
        return f"<Practitioner(name={self.name}, specialty={self.specialty}, hospital={self.hospital})>"
