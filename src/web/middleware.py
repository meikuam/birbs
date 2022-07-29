import datetime
from typing import List
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from src.time.time import local_now


class CheckMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
            register_endpoint: str,
            allowed_endpoints: List[str]
    ):
        super().__init__(app)
        self.register_endpoint = register_endpoint if register_endpoint[-1] == "/" else f"{register_endpoint}/"

        self.register_endpoint_timestamps: datetime.date = [local_now()]
        self.register_endpoint_timestamps_max_len = 10
        self.cooldown_date = local_now()
        self.cooldown_timedelta = datetime.timedelta(minutes=0, seconds=10)

        # process endpoint paths
        allowed_endpoints = list(set([endpoint.split("{")[0] for endpoint in allowed_endpoints]))
        allowed_endpoints = ["/".join(endpoint.split("/")[:3]) for endpoint in allowed_endpoints]
        allowed_endpoints = [endpoint if endpoint[-1] == "/" else f"{endpoint}/" for endpoint in allowed_endpoints]
        self.allowed_endpoints = allowed_endpoints
        print("allowed endpoints", self.allowed_endpoints)
        self.ban_ips = set()

    async def dispatch(self, request: Request, call_next):
        # check if client not in ban list
        client_ip = request.scope["client"][0]
        if client_ip in self.ban_ips:
            return Response(status_code=status.HTTP_403_FORBIDDEN)

        # check if client request allowed endpoints
        request_path = request.scope["path"]
        request_path = request_path if request_path[-1] == "/" else f"{request_path}/"
        check_request_path = "/".join(request_path.split("/")[:3])
        check_request_path = check_request_path if check_request_path[-1] == "/" else f"{check_request_path}/"

        if check_request_path not in self.allowed_endpoints:
            reason = "not in allowed endpoints"
            print(f"ban ip: {client_ip} {reason}", "path", request.scope["path"], "client", request.scope["client"], "params", request.query_params)
            self.ban_ips.add(client_ip)
            return Response(status_code=status.HTTP_403_FORBIDDEN)
        # check "/" endpoint
        if request_path == "/" and len(request.query_params) > 0:
            reason = "strange / path query params"
            print(f"ban ip: {client_ip} {reason}", "path", request.scope["path"], "client", request.scope["client"], "params", request.query_params)
            self.ban_ips.add(client_ip)
            return Response(status_code=status.HTTP_403_FORBIDDEN)
        # check register endpoint
        if request_path == self.register_endpoint:
            current_date = local_now()
            self.append_register_timestamp(current_date)
            if current_date < self.cooldown_date:
                return Response(status_code=status.HTTP_403_FORBIDDEN)

            if (self.register_endpoint_timestamps[-1] - self.register_endpoint_timestamps[0]).total_seconds() < datetime.timedelta(seconds=10).total_seconds():
                self.cooldown_date = current_date + self.cooldown_timedelta
                print(f"set cooldown date: {self.cooldown_date}")
                return Response(status_code=status.HTTP_403_FORBIDDEN)


        # process the request and get the response
        response = await call_next(request)

        return response

    def append_register_timestamp(self, timestamp):
        self.register_endpoint_timestamps.append(timestamp)
        if len(self.register_endpoint_timestamps) > self.register_endpoint_timestamps_max_len:
            del self.register_endpoint_timestamps[0]
