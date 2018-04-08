from property import Property
from util import get_valid_input as validate

class Apartment(Property):
    valid_laundries = ("coin", "ensuite", "none")
    valid_balconies = ("yes", "no", "solarium")

    def __init__(self, balcony='', laundry='', **kwargs):
        super().__init__(**kwargs)
        self.balcony = balcony
        self.laundry = laundry

    def display(self):
        super().display()
        print("APARTMENT DETAILS")
        print("laundry: %s" % self.laundry)
        print("has balcony: %s" % self.balcony)

    def prompt_init():
        #Run the Properties' prompt_init first
        parent_init = Property.prompt_init()
        laundry = validate( "What laundry facilities does the propery have?", Apartment.valid_laundries )
        balcony = validate( "Does the property have a balcony? ", Apartment.valid_balconies )
            #Update the parent's init dictionary with new values below
            parent_init.update({
                "laundry": laundry,
                "balcony": balcony
            })
            return parent_init
    prompt_init = staticmethod(prompt_init)