import json
import os
import pickle
import sys

from collections import defaultdict
from typing import Optional

import requests
from web3 import Web3
from datetime import datetime
import argparse

from web3.contract import Contract

from abi_extractor import extract_contract_abi
from timelaps_render import render_timelapse_frames, TimelapseSettings

# basepaint contract address
CONTRACT_ADDRESS = '0xBa5e05cb26b78eDa3A2f8e3b3814726305dcAc83'
# Hardcode value, took from here:
# https://basescan.org/address/0xBa5e05cb26b78eDa3A2f8e3b3814726305dcAc83
# by pressing on ContractCreator transaction link : at txn 0x4f9052feb5b3b20f79fa...
# https://basescan.org/tx/0x4f9052feb5b3b20f79fabc175438824badebcf840e478f36b0f3731ae524e14b
CONTRACT_CREATION_BLOCK = 2385188
# This value is valid on the time of writing,
# if you are getting ValueError: {'code': -32000, 'message': 'block range too large'}
# you should lower this value
EVENT_LOG_MAX_BLOCKS_INTERVAL = 2000


def load_contract_abi(use_latest: bool = False) -> dict:
    if use_latest:
        return extract_contract_abi(CONTRACT_ADDRESS)
    else:
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        path_to_abi = os.path.join(script_dir, 'resources', 'contract_abi.json')

        with open(path_to_abi, 'r') as f:
            return json.load(f)


def retrieve_day_theme_and_palette(day_number: int) -> tuple:
    """
    Fetch theme and palette for a specific day.
    """
    url = f'https://basepaint.xyz/api/theme/{day_number}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['palette'], response.json()['theme']


def retrieve_contract_paint_events(w3: Web3, contract: Contract, latest_block: int) -> tuple:
    """
    Fetch painted events from the contract.
    """
    CACHE_DIR = ".cache"
    CACHE_FILE = "paint_events_cache.pkl"

    day2paint_events = defaultdict(list)
    day2block = {}
    start_from_block = CONTRACT_CREATION_BLOCK

    # Check if there is a cache at cwd/.cache
    cache_path = os.path.join(CACHE_DIR, CACHE_FILE)
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            day2paint_events, day2block = pickle.load(f)
            start_from_block = max(day2block.values()) + 1  # +1 to start from the next block

    for i in range(start_from_block, latest_block, EVENT_LOG_MAX_BLOCKS_INTERVAL):
        try:
            painted_events = contract.events.Painted.get_logs(fromBlock=i, toBlock=i + EVENT_LOG_MAX_BLOCKS_INTERVAL)
        except ValueError:
            raise Exception("Update EVENT_LOG_MAX_BLOCKS_INTERVAL constant")

        for event in painted_events:
            if event.args.day not in day2block:
                block_data = w3.eth.get_block(event.blockNumber)
                day2block[event.args.day] = block_data['timestamp']
            pixels = event.args.pixels
            for x, y, color_index in zip(pixels[0::3], pixels[1::3], pixels[2::3]):
                day2paint_events[event.args.day].append((x, y, color_index))

    try:
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        with open(cache_path, "wb") as f:
            pickle.dump((day2paint_events, day2block), f)
    except (PermissionError, FileExistsError, OSError):
        pass

    return day2paint_events, day2block


def connect_to_web3(provider_url: str) -> Web3:
    """Initialize a Web3 connection."""
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Base network")
    return w3


def generate_timelapse_video(output_path: str,
                             day_number: int,
                             day2block: dict,
                             painted_events: dict,
                             timelapse_settings: TimelapseSettings):
    timestamp = datetime.utcfromtimestamp(day2block.get(day_number))
    formatted_timestamp = timestamp.strftime('%Y-%m-%d') if timestamp else "UNKNOWN_DATE"

    palette, theme = retrieve_day_theme_and_palette(day_number)
    absolute_output_path = os.path.join(os.getcwd(), output_path)
    os.makedirs(absolute_output_path, exist_ok=True)

    video_path = os.path.join(absolute_output_path, f"{formatted_timestamp}_#{day_number}_{theme}.mp4")

    render_timelapse_frames(video_path, painted_events[day_number], palette, timelapse_settings)


def main(output_path: str, day_number: Optional[int], timelapse_settings: TimelapseSettings):
    w3 = connect_to_web3('https://mainnet.base.org')
    abi = load_contract_abi()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    latest_block = w3.eth.get_block('latest')['number']
    painted_events, day2block = retrieve_contract_paint_events(w3, contract, latest_block)
    if day_number is None:
        # get the day number from contract and loop through each day
        day_number = contract.functions.today().call()
        for i in range(1, day_number + 1):
            generate_timelapse_video(output_path, i, day2block, painted_events, timelapse_settings)
    else:
        generate_timelapse_video(output_path, day_number, day2block, painted_events, timelapse_settings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a timelapse for a BasePaint day.')
    parser.add_argument('-o', '--output', help='Output directory', default="./output")
    parser.add_argument('-d', '--day_number', type=int, help='The day number for the timelapse.')
    parser.add_argument('--scale_factor', type=int, default=5, help='Scale factor for the video.')
    parser.add_argument('--frame_rate', type=int, default=30, help='Frame rate of the video.')
    parser.add_argument('--duration', type=int, default=30, help='Desired duration of the video in seconds.')
    parser.add_argument('--use-latest-abi', action='store_true',
                        help='Fetch the latest ABI from the API instead of using the saved version.')

    args = parser.parse_args()
    main(args.output, args.day_number, TimelapseSettings(args.scale_factor, args.frame_rate, args.duration))
