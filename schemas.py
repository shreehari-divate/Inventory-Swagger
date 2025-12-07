from marshmallow import Schema,fields

class User_Schema(Schema):

    user_id = fields.Str()
    user_name = fields.Str()