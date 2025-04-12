class Cola:
    def __init__(self):
        self.items = []

    def enqueue(self, item_id):
        self.items.append(item_id)

    def dequeue(self):
        return self.items.pop(0) if self.items else None

    def first(self):
        return self.items[0] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
