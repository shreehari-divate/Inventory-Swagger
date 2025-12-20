from marshmallow import Schema,fields

class User_Schema(Schema):

    user_id = fields.Str()
    user_name = fields.Str()

class User_Create_Schema(Schema):
    user_name = fields.Str(required=True)
    user_password = fields.Str(required=True)    


class User_reset_password(Schema):
    user_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

class Token_Schema(Schema):
    user_password = fields.Str(required=True)    