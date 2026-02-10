import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI


class AppConfig:
    """
    A class to load and store application settings from environment variables.
    """

    balance_sheet = "BALANCE_SHEET"
    income_statement = "INCOME_STATEMENT"
    asset = "ASSET"
    liability = "LIABILITY"
    equity = "EQUITY"
    revenue = "REVENUE"
    expense = "EXPENSE"
    current_asset = "CURRENT_ASSET"
    non_current_asset = "NON_CURRENT_ASSET"
    current_liability = "CURRENT_LIABILITY"
    non_current_liability = "NON_CURRENT_LIABILITY"
    earned_capital = "EARNED_CAPITAL"
    reserves = "RESERVES"
    deductions = "DEDUCTIONS"
    contributed_capital = "CONTRIBUTED_CAPITAL"
    operating_revenue = "OPERATING_REVENUE"
    non_operating_revenue = "NON_OPERATING_REVENUE"
    operating_expense = "OPERATING_EXPENSE"
    non_operating_expense = "NON_OPERATING_EXPENSE"

    tangible_fixed_assets = "TANGIBLE_FIXED_ASSETS"
    intangible_assets = "INTANGIBLE_ASSETS"
    accounts_receivable_and_prepayments = "ACCOUNTS_RECEIVABLE_PREPAYMENTS"
    cash_and_bank_balances = "CASH_BANK"
    share_capital = "SHARE_CAPITAL_RESERVES"
    shareholders_current_account = "SHAREHOLDERS_CURRENT_ACCOUNT"
    trade_and_other_payables = "TRADE_AND_OTHER_PAYABLES"
    cost_of_goods_sold = "COST_OF_GOODS_SOLD"
    administration_and_other_expenses = "ADMIN_AND_OTHER_EXPENSES"
    loan_and_advances = "LOAN_AND_ADVANCES"
    distribution_expenses = "DISTRIBUTION_EXPENSES"
    inventory = "INVENTORY"
    foreign_exchange_gain_or_loss = "FOREIGN_EXCHANGE_GAIN_OR_LOSS"
    unbilled_revenue = "UNBILLED_REVENUE"
    dividend_declared_and_paid = "DIVIDEND_DECLARED_AND_PAID"
    earnings_per_share = "EARNINGS_PER_SHARE"
    opening_stock = "OPENING_STOCK"
    closing_stock = "CLOSING_STOCK"
    purchases = "PURCHASES"
    provision="PROVISIONS"

    accumulated_depreciation = "accumulated_depreciation"
    cost = "COST"
    amortization = "AMORTIZATION"
    trade_debtors = "TRADE_DEBTORS"
    other_receivables = "OTHER_RECEIVABLES"
    salaries_and_benefits = "SALARIES_AND_BENEFITS"
    management_remuneration = "MANAGEMENT_REMUNERATION"

    is_deleted = "is_deleted"
    revaluation_gain_on_land = "REVALUATION GAIN ON LAND"
    soce_share_capital = "SHARE_CAPITAL"
    share_premium = "SHARE_PREMIUM"
    revaluation_reserves = "REVALUATION_RESERVES"
    retained_earning = "RETAINED_EARNING"
    

    def __init__(self):
        # Load environment variables from a .env file if it exists
        dotenv_path = find_dotenv()
        if not dotenv_path:
            raise FileNotFoundError(
                ".env file not found in the current directory or parent directories."
            )
        load_dotenv(dotenv_path)

        # Load variables from the environment

        # self.DEBUG = self._get_env_variable('DEBUG', optional=True, default='False').lower() in ('true', '1', 't')
        self.LANGSMITH_TRACING = self._get_env_variable(
            "LANGSMITH_TRACING", optional=True, default="False"
        ).lower() in ("true", "1", "t")
        self.LANGSMITH_ENDPOINT = self._get_env_variable(
            "LANGSMITH_ENDPOINT", optional=True
        )
        self.LANGCHAIN_API_KEY = self._get_env_variable(
            "LANGCHAIN_API_KEY", optional=True
        )
        self.LANGSMITH_PROJECT = self._get_env_variable(
            "LANGSMITH_PROJECT", optional=True
        )
        self.OPENAI_API_KEY = self._get_env_variable("OPENAI_API_KEY")
        # self.GEMINI_API_KEY = self._get_env_variable("GEMINI_API_KEY", optional=True)
        self.TAVILY_API_KEY = self._get_env_variable("TAVILY_API_KEY", optional=True)
        self.GROQ_API_KEY = self._get_env_variable("GROQ_API_KEY", optional=True)
        self.SERPER_API_KEY = self._get_env_variable("SERPER_API_KEY", optional=True)
        self.OPENAI_MODEL = self._get_env_variable("OPENAI_MODEL")
        # self.GEMINI_MODEL = self._get_env_variable("GEMINI_MODEL", optional=True)
        self.POSTGRES_DB = self._get_env_variable("POSTGRES_DB", optional=True)
        self.POSTGRES_USER = self._get_env_variable("POSTGRES_USER", optional=True)
        self.POSTGRES_PASSWORD = self._get_env_variable(
            "POSTGRES_PASSWORD", optional=True
        )
        self.DB_HOST = self._get_env_variable(
            "DB_HOST", optional=True, default="localhost"
        )
        self.DB_PORT = self._get_env_variable("DB_PORT", optional=True, default="5432")

    def _get_env_variable(self, var_name, optional=False, default=None):
        """
        Get the environment variable or raise an error if not found unless optional.
        """
        value = os.getenv(var_name, default)
        if value is None and not optional:
            raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
        return value

    def get_gpt4_llm(self, temperature=0):
        """
        Get a GPT-4 LLM instance.
        """
        return ChatOpenAI(
            model="gpt-4o", api_key=self.OPENAI_API_KEY, temperature=temperature
        )

    def get_gpt4_mini_llm(self, temperature=0):
        """
        Get a GPT-4 Mini LLM instance.
        """
        return ChatOpenAI(
            model="gpt-4o-mini", api_key=self.OPENAI_API_KEY, temperature=temperature
        )

    # def get_gemini(self, temperature=0):
    #     """
    #     Get a gemini instance
    #     """
    #     return ChatGoogleGenerativeAI(
    #         model="gemini-2.5-flash",
    #         api_key=self.GEMINI_API_KEY,
    #         temperature=temperature,
    #     )

    def get_groq(self, temperature=0):
        """
        Get a groq instance
        """
        return ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=self.GROQ_API_KEY,
            temperature=temperature,
        )

    def get_database_url(self):
        """
        Construct and return the database URL using environment variables.

        Returns:
            str: The database URL in the format:
                 postgresql://<user>:<password>@<host>:<port>/<database>
            None: If required database environment variables are missing.

        Raises:
            EnvironmentError: If any required environment variable is missing.
        """
        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
            raise EnvironmentError(
                "Required database environment variables (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) are missing."
            )

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )


if __name__ == "__main__":
    settings = AppConfig()
    # gpt4_llm = settings.get_gpt4_llm()
    # gpt4_mini_llm = settings.get_gpt4_mini_llm()
    # print(f"Email: {settings.EMAIL}")
    # print("GPT-4 LLM:", gpt4_llm)
    # print("GPT-4 Mini LLM:", gpt4_mini_llm)
