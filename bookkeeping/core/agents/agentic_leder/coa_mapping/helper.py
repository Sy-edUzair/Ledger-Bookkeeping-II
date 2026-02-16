from __future__ import annotations
import logging
from typing import List, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from bookkeeping.core.settings import AppConfig
from .prompts import system_prompt_coa_mapping_agent, human_prompt_coa_mapping_agent

settings = AppConfig()
logger = logging.getLogger(__name__)

AccountClass = Literal["ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"]


class AccountRef(BaseModel):
    account_id: str
    account_name: str
    account_code: int
    account_role: str
    account_class: AccountClass


class MappingPair(BaseModel):
    debit_account: AccountRef
    credit_account: AccountRef


class COAMappingResult(BaseModel):
    primary: MappingPair
    alternatives: List[MappingPair] = Field(default_factory=list)


coa_mapping_parser = PydanticOutputParser(pydantic_object=COAMappingResult)

def build_coa_mapping_chain(llm):
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
    ).partial(format_instructions=coa_mapping_parser.get_format_instructions())

    return prompt | llm | StrOutputParser()


def manual_repair_to_schema(llm, bad_output: str) -> str:
    repair_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Convert the content into VALID JSON that matches this schema exactly:\n"
                "{format_instructions}\n"
                "Rules:\n"
                "- JSON only\n"
                "- No markdown\n"
                "- No explanations\n",
            ),
            ("human", "Content to fix:\n{bad_output}"),
        ]
    ).partial(format_instructions=coa_mapping_parser.get_format_instructions())

    repair_chain = repair_prompt | llm | StrOutputParser()
    return repair_chain.invoke({"bad_output": bad_output})

def _dedupe_and_limit_alternatives(result: COAMappingResult, limit: int = 2) -> COAMappingResult:
    """
    Ensure alternatives are:
    - not identical to primary
    - unique among themselves
    - capped at `limit`
    """
    primary_sig = (
        result.primary.debit_account.account_id,
        result.primary.credit_account.account_id,
    )

    seen = {primary_sig}
    cleaned: List[MappingPair] = []

    for alt in result.alternatives:
        sig = (alt.debit_account.account_id, alt.credit_account.account_id)
        if sig in seen:
            continue
        seen.add(sig)
        cleaned.append(alt)
        if len(cleaned) >= limit:
            break

    result.alternatives = cleaned
    return result

def map_transaction_to_coa(transaction: dict, chart_of_accounts: list[dict]) -> dict:
    """
    Maps a validated transaction to debit/credit accounts from entity-bound COA.
    - transaction: validated intent dict
    - chart_of_accounts: list of JSON-safe accounts from fetch tool
    """

    llm = settings.get_gpt4_mini_llm(temperature=0.0)
    chain = build_coa_mapping_chain(llm)

    raw = chain.invoke(
        {
            "system_prompt": system_prompt_coa_mapping_agent,
            "human_prompt": human_prompt_coa_mapping_agent.format(
                transaction=transaction,
                chart_of_accounts=chart_of_accounts,
            ),
        }
    )

    try:
        parsed: COAMappingResult = coa_mapping_parser.parse(raw)
    except Exception as e:
        logger.error(f"COA MAPPING PARSE FAILED (first pass): {e}")
        fixed = manual_repair_to_schema(llm, raw)
        parsed = coa_mapping_parser.parse(fixed)

    parsed = _dedupe_and_limit_alternatives(parsed, limit=2)
    return parsed.model_dump()
