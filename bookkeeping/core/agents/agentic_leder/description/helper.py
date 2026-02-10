# helper.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel
from typing import Optional, Literal
import logging
from datetime import date

from .prompts import (
    system_prompt_description_agent,
    human_prompt_description_agent,
)

from bookkeeping.core.settings import AppConfig

settings = AppConfig()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Schema
# -------------------------

class StructuredTransaction(BaseModel):
    transaction_date: Optional[date]
    amount: Optional[float]
    currency: Optional[str]
    particular: Optional[str]
    description: Optional[str]
    transaction_type: Optional[
        Literal["ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"]
    ]
    payment_method: Optional[str]

structured_txn_parser = PydanticOutputParser(
    pydantic_object=StructuredTransaction
)

# -------------------------
# Chain Builder
# -------------------------

def build_description_chain(llm):
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
        format_instructions=structured_txn_parser.get_format_instructions()
    )

    return prompt | llm | StrOutputParser()

# -------------------------
# Manual Repair
# -------------------------

def manual_repair_to_schema(llm, bad_output: str) -> str:
    repair_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Convert the content into VALID JSON that matches this schema exactly:\n"
                "{format_instructions}\n"
                "Rules:\n"
                "- Return JSON only\n"
                "- No markdown\n"
                "- No explanations\n",
            ),
            ("human", "Content to fix:\n{bad_output}"),
        ]
    ).partial(
        format_instructions=structured_txn_parser.get_format_instructions()
    )

    repair_chain = repair_prompt | llm | StrOutputParser()
    return repair_chain.invoke({"bad_output": bad_output})

# -------------------------
# Public Helper
# -------------------------

def structure_transaction(transaction_text: str) -> dict:
    """
    Converts raw transaction text into structured accounting JSON.
    """

    llm = settings.get_gpt4_mini_llm(temperature=0.1)
    chain = build_description_chain(llm)

    system_prompt = system_prompt_description_agent
    human_prompt = human_prompt_description_agent.format(
        transaction_text=transaction_text
    )

    try:
        raw = chain.invoke(
            {
                "system_prompt": system_prompt,
                "human_prompt": human_prompt,
            }
        )

        try:
            parsed: StructuredTransaction = structured_txn_parser.parse(raw)
        except Exception:
            fixed = manual_repair_to_schema(llm, raw)
            parsed = structured_txn_parser.parse(fixed)

        return parsed.model_dump(mode="json")

    except Exception as e:
        logger.error(f"STRUCTURING FAILED: {e}")
        return {}
