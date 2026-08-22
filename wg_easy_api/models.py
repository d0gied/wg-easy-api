from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_serializer, field_validator

ClientID = int


class Client(BaseModel):
    id: ClientID
    userId: int
    interfaceId: str
    name: str
    ipv4Address: str
    ipv6Address: str
    preUp: str
    postUp: str
    preDown: str
    postDown: str
    publicKey: str
    privateKey: str | None = None  # ommited in GET api/client
    preSharedKey: str | None = None  # ommited in GET api/client
    expiresAt: datetime | None
    allowedIps: str | None
    serverAllowedIps: list[str]
    firewallIps: str | None
    persistentKeepalive: int
    mtu: int
    jC: int
    jMin: int
    jMax: int
    i1: int | None
    i2: int | None
    i3: int | None
    i4: int | None
    i5: int | None
    dns: str | None
    serverEndpoint: str | None
    enabled: bool
    createdAt: datetime
    updatedAt: datetime
    # ommited in GET api/client/{id} if client.enabled == False
    endpoint: str | None = None

    @field_validator("createdAt", "updatedAt", "expiresAt", mode="before")
    @classmethod
    def parse_datetime(cls, value: object):
        if not isinstance(value, str):
            return value
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    @field_serializer("createdAt", "updatedAt", "expiresAt")
    def serialize_datetime(self, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class ClientPost(BaseModel):
    name: str
    expiresAt: datetime | None = None


class ClientPostReturn(BaseModel):
    success: bool
    clientId: ClientID


class ApiErrorModel(BaseModel):
    error: bool
    url: HttpUrl
    statusCode: int
    statusMessage: str
    message: str
    data: dict[str, str] | None = None


class ApiError(Exception):
    details: ApiErrorModel

    def __init__(self, details: ApiErrorModel):
        self.details = details
        super().__init__(self.details.message)


class Success(BaseModel):
    success: bool
