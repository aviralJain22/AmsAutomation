from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ams360_url: str = Field(..., alias="AMS360_URL")
    ams360_url_if_login: str = Field(..., alias='AMS360_URL_IF_LOGIN')
    agency: str = Field(..., alias="AGENCY")
    username: str = Field(..., alias="AMS360_USERNAME")
    password: str = Field(..., alias="AMS360_PASSWORD")
    customer_name: str = Field("Seymour, James M", alias="CUSTOMER_NAME")
    customer_address: str = Field("", alias="CUSTOMER_ADDRESS")
    output_excel: str = Field("output.xlsx", alias="OUTPUT_EXCEL")
    fee_charge_type: str = Field("Agency Fee", alias="FEE_CHARGE_TYPE")
    fee_amount: str = Field("0.00", alias="FEE_AMOUNT")
    customer_url: str = Field(..., alias='CUSTOMER_URL')

    model_config = {
        "env_file": Path(__file__).parent / ".env",
        "populate_by_name": True,
        "extra": "ignore",          # ignore stray OS env vars like Windows USERNAME
    }


settings = Settings()
