from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ams360_url: str = Field(..., alias="AMS360_URL")
    ams360_url_if_login: str = Field(..., alias='AMS360_URL_IF_LOGIN')
    agency: str = Field(..., alias="AGENCY")
    username: str = Field(..., alias="AMS360_USERNAME")
    password: str = Field(..., alias="AMS360_PASSWORD")
    output_excel: str = Field("output.xlsx", alias="OUTPUT_EXCEL")
    fee_charge_type: str = Field("Agency Fee", alias="FEE_CHARGE_TYPE")
    fee_amount: str = Field("0.00", alias="FEE_AMOUNT")
    policy_action: str = Field("Renew", alias="POLICY_ACTION")  # "Renew" or "Endorse"
    customer_url: str = Field(..., alias='CUSTOMER_URL')
    # Customer
    customer_name: str = Field(..., alias="CUSTOMER_NAME")
    customer_address: str = Field("", alias="CUSTOMER_ADDRESS")
    customer_city: str = Field("", alias="CUSTOMER_CITY")
    customer_state: str = Field("", alias="CUSTOMER_STATE")
    customer_zip: str = Field("", alias="CUSTOMER_ZIP")
    contact_full_name: str = Field("", alias="CONTACT_FULL_NAME")
    # Policy
    policy_number: str = Field(..., alias="POLICY_NUMBER")
    effective_date: str = Field("", alias="EFFECTIVE_DATE")
    expiration_date: str = Field("", alias="EXPIRATION_DATE")
    policy_premium: str = Field("", alias="POLICY_PREMIUM")
    carrier_fee: str = Field("", alias="CARRIER_FEE")
    policy_type: str = Field("", alias="POLICY_TYPE")
    date_of_purchase: str = Field("", alias="DATE_OF_PURCHASE")
    method_of_payment: str = Field("", alias="METHOD_OF_PAYMENT")
    endorsement_number: str = Field("", alias="ENDORSEMENT_NUMBER")
    endorsement_description: str = Field("", alias="ENDORSEMENT_DESCRIPTION")
    total_gross_annual_premium: str = Field("", alias="TOTAL_GROSS_ANNUAL_PREMIUM")
    installment_finance: str = Field("", alias="INSTALLMENT_FINANCE")
    marketing_type: str = Field("", alias="MARKETING_TYPE")

    model_config = {
        "env_file": Path(__file__).parent / ".env",
        "populate_by_name": True,
        "extra": "ignore",          # ignore stray OS env vars like Windows USERNAME
    }


settings = Settings()
