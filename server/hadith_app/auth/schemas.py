from marshmallow import Schema, fields, validate


class CredentialsSchema(Schema):
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=20),
        validate.Regexp('^[A-Za-z0-9_]+$', error="Username must contain only letters, numbers, and underscores")
    ])
    password = fields.Str(required=True, validate=[
        validate.Length(min=8, max=20),
        validate.Regexp('^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@!_&])[A-Za-z\\d@!_&]{8,}$',
                        error="Password must contain letters, numbers, and at least one special character (@!_&)")
    ])
