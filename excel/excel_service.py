from __future__ import annotations

from pathlib import Path

import openpyxl
from openpyxl import Workbook

from config.constants import EXCEL_HEADERS
from config.settings import settings
from excel.models import CustomerInfo, FeeInfo, PolicyInfo
from helpers.logger import get_logger

logger = get_logger(__name__)


class ExcelService:
    def get_fee_info(self) -> FeeInfo:
        # TODO Phase 2: read charge_type + amount row-by-row from input Excel file
        return FeeInfo(charge_type=settings.fee_charge_type, amount=settings.fee_amount)

    def get_customer(self) -> CustomerInfo:
        # TODO Phase 2: read name + address row-by-row from input Excel file
        return CustomerInfo(name=settings.customer_name, address=settings.customer_address)

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
