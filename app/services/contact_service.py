class ContactService:
    @staticmethod
    def send_contact_message(data):
        # In a real application, this would send an email or save to a database
        print(f"Contact Message Received: Name: {data['name']}, Email: {data['email']}, Message: {data['message']}")
        return {"message": "Contact message sent successfully!"}
