# Backend application for automating retail purchasing 

### Project Goal:  
Develop and configure a retail purchasing automation system, including data modeling, product import features, and API view implementation.

### Application Overview
The app exclusively uses API requests for all interactions.

### Service Description  
The service enables users to order products from multiple stores. Product catalogs, pricing, and stock information are loaded from files in a standardized format.

Users can compile an order (shopping cart) by adding products from different stores, all displayed in a unified catalog. If a product is available in multiple stores, users can select which store to purchase it from. Since prices may vary between stores, this selection will affect the total order amount.

After confirming the order on the checkout page, the order is saved in the database with the status "Created".

When the order status changes to "Confirmed", the user receives an email or phone notification about the update. 

