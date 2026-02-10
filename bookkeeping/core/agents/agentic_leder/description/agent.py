# agent.py
import logging
from .helper import structure_transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def description_agent(transaction_text: str) -> dict:
    """
    DESCRIPTION / STRUCTURING AGENT
    Raw text → structured accounting JSON
    """

    logger.info("STARTING DESCRIPTION AGENT")

    structured_txn = structure_transaction(transaction_text)

    logger.info("DESCRIPTION AGENT COMPLETED")

    return structured_txn


if __name__ == "__main__":
    # test_input = "Paid office rent of 2,000 AED via bank transfer on 5th Jan"
    # test_input = "Bought pens and paper for 2,000 USD on 5th Jan"
    #test_input = "Received 1,200 USD from client for website design services on Jan 12"    
    
    # Currency backend se aayegi
    # Add valid payment methods in prompt 
    test_input = "Owner invested 50,000 as initial capital on 1-7-2026"
    result = description_agent(test_input)

    import json
    print(json.dumps(result, indent=2))
    try:
        with open("initial_transaction.json", 'w') as json_file:
            json.dump(result, json_file, indent=4)

    except IOError as e:
        print(f"Error writing to file: {e}")
            
