from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional
from textwrap import dedent
import json

categories = [item["category"] for item in json.load(open("data/categories.json"))]


class Transaction(BaseModel):
    merchant_name: str
    merchant_category: list[str]
    department: str
    location: str
    amount: float
    spend_program_name: str
    trip_name: Optional[str] = None
    expense_category: str

    def generate_transaction(self):
        return dedent(f"""
        Name : {self.merchant_name}
        Category: {", ".join(self.merchant_category)}
        Department: {self.department}
        Location: {self.location}
        Amount: {self.amount}
        Card: {self.spend_program_name}
        Trip Name: {self.trip_name if self.trip_name else "unknown"}
        """)

    @field_validator("expense_category")
    @classmethod
    def validate_expense_category(cls, v, info: ValidationInfo):
        if not info.context or not info.context["category"]:
            return v
        return info.context["category"]["category"]
