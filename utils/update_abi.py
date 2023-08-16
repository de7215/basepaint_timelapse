import json

from abi_extractor import extract_contract_abi
from create_timelapse import CONTRACT_ADDRESS

abi = extract_contract_abi(CONTRACT_ADDRESS)
with open('../resources/contract_abi.json', 'w') as f:
    json.dump(abi, f, indent=4)
