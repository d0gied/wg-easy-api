from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Client(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    enabled: bool = Field(...)
    address: str = Field(...)
    public_key: str = Field(..., alias="publicKey")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(..., alias="updatedAt")
    expired_at: datetime | None = Field(..., alias="expiredAt")
    one_time_link: str | None = Field(..., alias="oneTimeLink")
    one_time_link_expires_at: datetime | None = Field(..., alias="oneTimeLinkExpiresAt")
    downloadable_config: bool = Field(..., alias="downloadableConfig")
    persistent_keepalive: int | None = Field(..., alias="persistentKeepalive")
    latest_handshake_at: datetime | None = Field(..., alias="latestHandshakeAt")
    transfer_rx: int | None = Field(..., alias="transferRx")
    transfer_tx: int | None = Field(..., alias="transferTx")
    endpoint: str | None = Field(...)

    @field_validator("persistent_keepalive", mode="before")
    def validate_persistent_keepalive(cls, v):
        if v == "off":
            return None
        return v


class Session(BaseModel):
    requires_password: bool = Field(..., alias="requiresPassword")
    authenticated: bool = Field(...)

class Success(BaseModel):
    success: bool = Field(...)