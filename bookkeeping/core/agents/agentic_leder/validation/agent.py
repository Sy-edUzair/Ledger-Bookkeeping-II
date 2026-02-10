# agent.py

import logging
from .helper import validate_transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validation_agent(structured_transaction: dict) -> dict:
    """
    VALIDATION AGENT
    Structured transaction → accounting validation result
    """

    logger.info("STARTING VALIDATION AGENT")

    result = validate_transaction(structured_transaction)

    logger.info(
        f"VALIDATION COMPLETED — "
        f"ERRORS: {len(result['errors'])} - "
        f"WARNINGS: {len(result['warnings'])}"
    )

    return result


if __name__ == "__main__":
    import json
    try:
        with open("initial_transaction.json", 'r') as json_file:
            data = json.load(json_file)
    except IOError as e:
        print(f"Error writing to file: {e}")

    result = validation_agent(data)
    print(json.dumps(result, indent=2))
    
    try:
        with open("validated_transaction.json", 'w') as json_file:
            json.dump(result, json_file, indent=4)
    except IOError as e:
        print(f"Error writing to file: {e}")
