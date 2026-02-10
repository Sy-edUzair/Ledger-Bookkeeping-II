from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel
from typing import List, Literal
import logging

from .prompts import (
    system_prompt_journal_entry_agent,
    human_prompt_journal_entry_agent,
)

from bookkeeping.core.settings import AppConfig

settings = AppConfig()
logger = logging.getLogger(__name__)

# -------------------------
# Schema
# -------------------------

class JournalLine(BaseModel):
    account_id: int
    side: Literal["DEBIT", "CREDIT"]
    amount: float

class JournalEntryPayload(BaseModel):
    lines: List[JournalLine]
    narration: str

journal_parser = PydanticOutputParser(
    pydantic_object=JournalEntryPayload
)

# -------------------------
# Builder
# -------------------------

def build_journal_chain(llm):
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
        format_instructions=journal_parser.get_format_instructions()
    )

    return prompt | llm | StrOutputParser()

# -------------------------
# Public Helper
# -------------------------

def build_journal_entry(
    transaction: dict,
    debit_account: dict,
    credit_account: dict,
) -> dict:
    """
    Builds a structured journal entry payload.
    NO posting, NO validation.
    """

    llm = settings.get_gpt4_mini_llm(temperature=0.0)
    chain = build_journal_chain(llm)

    raw = chain.invoke(
        {
            "system_prompt": system_prompt_journal_entry_agent,
            "human_prompt": human_prompt_journal_entry_agent.format(
                debit_account=debit_account,
                credit_account=credit_account,
                transaction=transaction,
            ),
        }
    )

    try:
        parsed = journal_parser.parse(raw)
        return parsed.model_dump()
    except Exception as e:
        logger.error(f"JOURNAL ENTRY PARSE FAILED: {e}")
        raise
