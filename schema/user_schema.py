from marshmallow import Schema,fields

class User_Schema(Schema):

    user_id = fields.Str()
    user_name = fields.Str()

class User_Create_Schema(Schema):
    user_name = fields.Str(required=True)
    password = fields.Str(required=True)    