# Backend application for automating retail purchasing 

### Project Goal:  
Develop and configure a retail purchasing automation system, including data modeling, product import features, and API view implementation.

### Application Overview
The app exclusively uses API requests for all interactions.
  
### Service Description  
The service enables users to order products from multiple stores. Product catalogs, pricing, and stock information are loaded from files in a standardized format.

Users can compile an order (shopping cart) by adding products from different stores, all displayed in a unified catalog. 

After confirming the order on the checkout page, the order is saved in the database with the status "Created".

When the order status changes to "Confirmed", the user receives an email or phone notification about the update.   
  
### Core entities  
1. User 
2. Shop
3. Category
4. Model
5. ProductInfo
6. Parameter
7. ProductParameter
8. Contact
9. DeliveryAddress
10. Order
11. OrderItem

### User 
To place an order, the user must register in the system by entering first name, last name, 
middle name (if available, optional field), username (the email address is used as the username), and password. 
An administrator user has the right to create administrator and superuser accounts through the system’s admin panel.
The user does not need to be authorized in the system to view the list of products.

### Shop 
The store has name and sometimes a website.

### Category
Categories have a name.  
Categories are linked to stores via a many-to-many relationship. 
Nested categories are not supported.
