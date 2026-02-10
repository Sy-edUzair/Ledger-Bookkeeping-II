# helper.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel
from typing import List, Optional, Literal
import logging
from datetime import date
from .prompts import (
    system_prompt_validation_agent,
    human_prompt_validation_agent,
)

from bookkeeping.core.settings import AppConfig

settings = AppConfig()
logger = logging.getLogger(__name__)

# -------------------------
# Schemas
# -------------------------

class ValidationError(BaseModel):
    field: str
    message: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    suggested_fix: Optional[str]

class ValidationResult(BaseModel):
    errors: List[ValidationError]
    warnings: List[ValidationError]

validation_parser = PydanticOutputParser(
    pydantic_object=ValidationResult
)

def run_rule_based_checks(txn: dict) -> list[ValidationError]:
    errors = []

    today = date.today()

    # ---- Date validation
    if txn.get("transaction_date"):
        try:
            txn_date = date.fromisoformat(txn["transaction_date"])
            if txn_date > today:
                errors.append(
                    ValidationError(
                        field="transaction_date",
                        code="FUTURE_DATE",
                        message="Transaction date cannot be later than today.",
                        severity="HIGH",
                        suggested_fix=None,
                    )
                )
        except ValueError:
            errors.append(
                ValidationError(
                    field="transaction_date",
                    code="INVALID_DATE_FORMAT",
                    message="Transaction date must be in YYYY-MM-DD format.",
                    severity="HIGH",
                    suggested_fix=None,
                )
            )

    # ---- Amount validation
    if txn.get("amount") is None or txn.get("amount") <= 0:
        errors.append(
            ValidationError(
                field="amount",
                code="INVALID_AMOUNT",
                message="Transaction amount must be greater than zero.",
                severity="HIGH",
                suggested_fix=None,
            )
        )
def run_llm_validation(txn: dict) -> ValidationResult:
    llm = settings.get_gpt4_mini_llm(temperature=0.0)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_prompt}\n\n"
                "Return your answer strictly in the following format:\n"
                "{format_instructions}",
            ),
            ("human", "{human_prompt}"),
        ]
    ).partial(
        format_instructions=validation_parser.get_format_instructions()
    )

    chain = prompt | llm | StrOutputParser()

    raw = chain.invoke(
        {
            "system_prompt": system_prompt_validation_agent,
            "human_prompt": human_prompt_validation_agent.format(
                transaction_json=txn
            ),
        }
    )

    try:
        result = validation_parser.parse(raw)
        return result
    except Exception as e:
        logger.error(f"LLM VALIDATION PARSE FAILED: {e}")
        return ValidationResult(
            errors=[
                ValidationError(
                    field="__system__",
                    code="LLM_FAILURE",
                    message="LLM validation failed. Manual review required.",
                    severity="HIGH",
                    suggested_fix=None,
                )
            ],
            warnings=[],
        )

def validate_transaction(txn: dict) -> dict:
    """
    Validates structured transaction for accounting correctness.
    """

    rule_errors = run_rule_based_checks(txn)
    llm_result = run_llm_validation(txn)
    print(llm_result)
    all_errors = {}
    if rule_errors != None and llm_result != None:
        all_errors = rule_errors + llm_result.errors
    elif rule_errors == None:
        all_errors = llm_result.errors
    elif llm_result.errors == None:
        all_errors = rule_errors
    else:
        all_errors=[]
    all_warnings = llm_result.warnings

    return {
        "errors": [e.model_dump() for e in all_errors],
        "warnings": [w.model_dump() for w in all_warnings],
    }
