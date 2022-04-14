class Door:
    """
    Модель для обьектов типа "Дверь"
    """
    id = None
    name = None
    price = None
    size = None
    color = None
    image = None

    def __init__(self, _id, name, price, size, color, image):
        self.id = _id
        self.name = name
        self.price = price
        self.size = size
        self.color = color
        self.image = image
