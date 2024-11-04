from marshmallow import Schema, fields, validate


class CredentialsSchema(Schema):
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=20)
    ])
    password = fields.Str(required=True, validate=[
        validate.Length(min=8, max=20)
    ])
