class Subtitle:
    def __init__(self, id, timestamps, text):
        # Store original id_line for potential reference, but we will overwrite it for output
        self.id = id
        self.timestamps = timestamps
        self.text = text

    def __str__(self):
        # Reconstruct the standard SRT block format
        return f"{self.id}\n{self.timestamps}\n{self.text}"
