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