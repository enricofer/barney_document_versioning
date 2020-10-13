class CorsMiddleware:
    def process_response(self, req, resp):
        response["Access-Control-Allow-Origin"] = "*"
        return response