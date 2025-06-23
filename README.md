# Backend application for automating retail purchasing  

[Project Goal](#project-goal)  
[Application Overview](#application-overview)  
[Service Description](#service-description)  
[Core entities](#core-entities)  
[Implementation of API views](implementation-of-api-views)
  

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

#### <ins> User </ins>  
To place an order, the user must register in the system by entering first name, last name, 
middle name (if available, optional field), username (the email address is used as the username), and password. 
An administrator user has the right to create administrator and superuser accounts through the system’s admin panel.
The user does not need to be authorized in the system to view the list of products.

#### <ins> Shop </ins>
The store has name and sometimes a website.

#### <ins> Category </ins>
Categories have a name.  
Categories are linked to stores via a many-to-many relationship. 
Nested categories are not supported.

#### <ins> Model </ins>
Product model has a name.  
A "many-to-one" relationship between the current product model and the category it belongs to.

#### <ins> ProductInfo </ins>
Represents detailed information about a specific product offering in the stor, includes:
- product name (display name for the item)
- reference to a generic product model 
- the shop offering the product
- quantity available in stock
- current selling price
- recommended retail price (RRP)

#### <ins> Parameter </ins>
Parameter model has a name. 
  
#### <ins> ProductParameter </ins>  
ProductParameter model contains parameter values of a specific product.
  
#### <ins> Contact </ins>  
Contact model stores user contacts: either phone or email, according to the user's choice. 
  
#### <ins> DeliveryAddress </ins>  
DeliveryAddress model stores information about user's delivery addresses. 
The model contains the following fields: city, street, building, block, structure, apartment. 
  
#### <ins> Order </ins>  
Order model contains information about user's order: order creation date, status and delivery address (a mandatory field for orders with status "Confirmed"). 
  
#### <ins> OrderItem </ins>  
OrderItem model contains information about the quantity of the product and also references the product’s selling shop, the user’s order, and the product information.

### Implementation of API views  
API Views for the main service pages:  
 • Registration
 • Authorization (Login)  
 • Get list of products  
 • Get product details  
 • Manage shopping cart (add/remove products)  
 • Add/remove delivery address  
 • Confirm order  
 • Get list of orders  
 • Get order details  
  
Documentation is available at: https://juliaromi.github.io/retail_purchasing_automation/ 
