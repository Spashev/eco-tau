from account.authentication import JWTAuthentication


class ProductMixins:
    def get_serializer_context(self):
        jwt = JWTAuthentication()
        user = jwt.authenticate(self.request)
        return {'user_id': user[0].id} if user is not None else None
