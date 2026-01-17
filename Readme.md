#INVENTORY MANAGAEMENT 

Inventory of a xyz company. User can login and place their order in bulk quanity by providing the product type, product and quantity.
Admin adds product according to their types, can delete/remove the product, update their quantity and perform other Crud operations. Admin also has previlage to look into the user and delete user if required.

User: 
* Created a Admin profile with unique name and password
* Created a user routes for user authentication 
* User can use inventory if they have account else create an account by using the Post api in user section 
* Only admin can view all users

Product:
* Added a collection for products which has id,name,type(enum),sku,timestamp,active(bool),quantity and price
* Created a route for inserting a product into the db
* Created a route for get call which displays all the product in the db

Fixed the user post such that only inauthroized users can create user 

created order routes
Order:
* Added get order routes
* Added post route such that it takes the current user and then takes a list of products to create a order.
* User can cancel the order by providing the user_id, order_id and valid reason to cancel the order. This order cancel will be a patch request.
* User can update the product quantity only through patch api
* User can check his order status through user_order_status api

Pending work is role base access to create user, get available product based on types order for orders. 
not necessary-(To delete the order/user user will request for deletion where delete will generate a unique code. Admin has privilage to delete the user/order by entering that unique code. Either use unique code or _id) will do if required as cancel is now patch not delete request.
Need to find a way how to change the status of payment_status, order_status
Need to add delivery status to order.