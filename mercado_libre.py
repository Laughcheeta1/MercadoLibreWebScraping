class Mercado_Libre_Object:
    def __init__(self, 
        title: str, 
        url: str,
        price: float, 
        currency: str, 
        condition: str,
        seller_name: str,
        first_image_url: str,
        ):
        self.title = title
        self.url = url
        self.price = price
        self.currency = currency
        self.condition = condition
        self.seller_name = seller_name
        self.first_image_url = first_image_url

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "price": self.price,
            "currency": self.currency,
            "condition": self.condition,
            "seller_name": self.seller_name,
            "first_image_url": self.first_image_url,
        }

    def __str__(self):
        return self.to_dict()
