from dataclasses import dataclass, fields
from typing import Literal


@dataclass
class CustomerInfo:
    name: str
    contact_full_name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""


@dataclass
class FeeInfo:
    charge_type: str
    amount: str


@dataclass
class PolicyInstruction:
    """Per-row instruction read from the input Excel file."""
    action: Literal["Renew", "Endorse", "Policy", "Receipt"]
    policy_number: str = ""
    effective_date: str = ""
    expiration_date: str = ""
    policy_premium: str = ""
    fee_amount: str = ""
    carrier_fee: str = ""
    policy_type: str = ""
    date_of_purchase: str = ""
    method_of_payment: str = ""
    endorsement_number: str = ""
    endorsement_description: str = ""
    total_gross_annual_premium: str = ""
    installment_finance: str = ""
    marketing_type: str = ""


@dataclass
class PolicyInfo:
    policy_number: str
    effective_date: str
    expiration_date: str
    premium: str
    status: str
    fees: str
    annualized_premium: str
    bill_method: str = ""
    customer_name: str = ""
    customer_address: str = ""

    def as_row(self) -> list:
        return [getattr(self, f.name) for f in fields(self)]
