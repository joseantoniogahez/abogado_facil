from pydantic import ConfigDict

from app.core.common.schema import ApplicationSchema


class CurrentPrincipal(ApplicationSchema):
    id: int
    email: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    display_name: str
    disabled: bool
    firm_id: int | None = None

    model_config = ConfigDict(frozen=True, from_attributes=True)
