class Mercado_Libre_Object:
    def __init__(self, 
        title: str, 
        url: str,
        price: float, 
        currency: str, 
        condition: str,
        seller_id: str,
        first_image_url: str,
        ):
        self.title = title
        self.url = url
        self.price = price
        self.currency = currency
        self.condition = condition
        self.seller_id = seller_id
        self.first_image_url = first_image_url

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "price": self.price,
            "currency": self.currency,
            "condition": self.condition,
            "seller_id": self.seller_id,
            "first_image_url": self.first_image_url,
        }


        