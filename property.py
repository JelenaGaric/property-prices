from datetime import datetime


class Property:
    def __init__(self, title: str,
                 location: str,
                 street: str,
                 size: float,
                 price: float,
                 price_per_size: float,
                 date_published: datetime,
                 under_construction: bool):
        self.title = title
        self.location = location
        self.street = street
        self.size = size
        self.price = price
        self.price_per_size = price_per_size
        self.date_published = date_published
        self.under_construction = under_construction

    def to_dict(self):
        return {
            'title': self.title,
            'location': self.location,
            'street': self.street,
            'size': self.size,
            'price': self.price,
            'price_per_size': self.price_per_size,
            'date_published': self.date_published,
            'under_construction': self.under_construction
        }
