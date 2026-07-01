from dataclasses import dataclass, fields


@dataclass
class CustomerInfo:
    name: str
    address: str


@dataclass
class FeeInfo:
    charge_type: str
    amount: str


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
