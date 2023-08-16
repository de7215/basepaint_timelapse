import json
import os
import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("It seems you don't have the 'dotenv' package installed.")
    print("Using 'dotenv' is considered a best practice as it allows you to:")
    print("1. Keep your configuration separate from your code, making your application more configurable and secure.")
    print("2. Avoid accidental exposure of secrets by storing them in an external "
          "'.env' file which can be added to .gitignore.")
    print("3. Easily manage and update your environment variables in a single file.")
    print("\nTo take advantage of these benefits, consider installing the 'dotenv' package using pip:\n")
    print("pip install python-dotenv")

BASESCAN_API_KEY = os.environ.get('BASESCAN_API_KEY')

if not BASESCAN_API_KEY:
    raise ValueError(
        "ERROR: The 'BASESCAN_API_KEY' environment variable is not set.\n"
        "To resolve this:\n"
        "1. Obtain an API key by registering at https://basescan.org/register\n"
        "2. Set the 'BASESCAN_API_KEY' environment variable with the obtained key.\n"
        "Consider using an .env file and the 'dotenv' package for better security "
        "and management of environment variables."
    )


def extract_contract_abi(contract_address: str) -> dict:
    """
    Fetch the Application Binary Interface (ABI) for a given contract address
    from the BaseScan API.

    Parameters:
        contract_address (str): The address of the contract for which the ABI
        needs to be retrieved.

    Returns:
        dict: The ABI of the contract as a dictionary.

    Raises:
        ValueError: If the ABI is not found for the given contract address.
    """
    url = (f'https://api.basescan.org/api?module=contract&action=getabi'
           f'&address={contract_address}&apikey={BASESCAN_API_KEY}')
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if not data.get('result'):
        raise ValueError("ABI not found for the given contract address")
    return json.loads(data['result'])
