from marshmallow import Schema, ValidationError, fields


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    remember_me = fields.Boolean(load_default=False)


class RequestPasswordResetSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.String(required=True)
    new_password = fields.String(required=True)


class VerifyTokenSchema(Schema):
    token = fields.String(required=True)


class UserCreateSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    group_ids = fields.List(fields.Integer(), load_default=[])


class UserPatchSchema(Schema):
    email = fields.Email(required=False)
    is_active = fields.Boolean(required=False)
    must_reset_password = fields.Boolean(required=False)


class GroupCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(load_default="")


class GroupPatchSchema(Schema):
    name = fields.String(required=False)
    description = fields.String(required=False)


class GroupMemberChangeSchema(Schema):
    user_id = fields.Integer(required=True)
    action = fields.String(required=True)


class GroupPermChangeSchema(Schema):
    permission = fields.String(required=True)
    action = fields.String(required=True)


def validate(schema, payload):
    try:
        return schema.load(payload)
    except ValidationError as exc:
        return exc.messages
