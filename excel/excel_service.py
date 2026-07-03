from __future__ import annotations

from pathlib import Path

import openpyxl
from openpyxl import Workbook

from config.constants import EXCEL_HEADERS
from config.settings import settings
from excel.models import CustomerInfo, FeeInfo, PolicyInfo, PolicyInstruction
from helpers.logger import get_logger

logger = get_logger(__name__)


class ExcelService:
    def get_customer(self) -> CustomerInfo:
        return CustomerInfo(
            name=settings.customer_name,
            contact_full_name=settings.contact_full_name,
            address=settings.customer_address,
            city=settings.customer_city,
            state=settings.customer_state,
            zip=settings.customer_zip,
        )

    def get_fee_info(self) -> FeeInfo:
        return FeeInfo(
            charge_type=settings.fee_charge_type,
            amount=settings.fee_amount,
        )

    def get_policy_instruction(self) -> PolicyInstruction:
        return PolicyInstruction(
            action=settings.policy_action,  # type: ignore[arg-type]
            policy_number=settings.policy_number,
            effective_date=settings.effective_date,
            expiration_date=settings.expiration_date,
            policy_premium=settings.policy_premium,
            fee_amount=settings.fee_amount,
            carrier_fee=settings.carrier_fee,
            policy_type=settings.policy_type,
            date_of_purchase=settings.date_of_purchase,
            method_of_payment=settings.method_of_payment,
            endorsement_number=settings.endorsement_number,
            endorsement_description=settings.endorsement_description,
            total_gross_annual_premium=settings.total_gross_annual_premium,
            installment_finance=settings.installment_finance,
            marketing_type=settings.marketing_type,
        )

    def write_policy(self, policy_info: PolicyInfo, path: str | None = None) -> None:
        output_path = Path(path or settings.output_excel)
        logger.info(f"Writing policy to Excel: {output_path}")

        if output_path.exists():
            wb = openpyxl.load_workbook(output_path)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(EXCEL_HEADERS)

        ws.append(policy_info.as_row())
        wb.save(output_path)
        logger.info(f"Policy data written to {output_path}")
