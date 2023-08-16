# BasePaint Timelapse Generator
Generate a video timelapse for BasePaint days with various configurable options. The script fetches painting events from the Base network and then uses this data to produce a video that simulates the painting activity in a time-lapsed manner.

## Getting Started
### Prerequisites
Python: This script requires Python 3.x.

Dependencies:

- requests: For making API requests.
- web3: To interact with the Ethereum network.
- cv2 (OpenCV): For video generation.
- numpy: To handle image arrays.
- imageio and imageio[ffmpeg]: For handling video frame writing and ensuring compatibility with various codecs.
- dotenv (Optional): For loading environment variables from a .env file.

Install them using pip:

```bash
pip install requests web3 opencv-python numpy python-dotenv imageio imageio[ffmpeg]
```
Note: If you don't want to use the dotenv package, you can skip its installation, but it is recommended for handling sensitive data like API keys securely.

Basescan API Key: 

This is required if you want to fetch the latest ABI from Basescan. You can get your API key by registering here.

### Configuration
(Recommended) Create a .env file in the same directory as your script and add your Basescan API Key:
```
BASESCAN_API_KEY=YourBasescanApiKeyHere
```
If you choose not to use a .env file, you can directly set the `BASESCAN_API_KEY` environment variable on your system.

### Usage
To run the script:

```bash
python create_timelapse.py [--day_number <day_number>] [--use-latest-abi] [--scale_factor <factor>] [--frame_rate <rate>] [--duration <seconds>]
```

Arguments:

- --day_number: Specifies the day number for the timelapse. If not provide will generate all the days.
- --use-latest-abi: (Optional) Use the latest ABI from Basescan API instead of the locally saved ABI. Requires BASESCAN_API_KEY.
- --scale_factor: (Optional) Scale factor for the video. Default is 5.
- --frame_rate: (Optional) Frame rate of the video. Default is 30.
- --duration: (Optional) Desired duration of the video in seconds. Default is 30.

### How it Works
- Fetch Contract ABI: The script either uses a locally stored ABI or fetches the latest ABI from Basescan based on the provided flag.

- Interact with the Ethereum Network: Using the web3 package, the script connects to the Base network and fetches painting events.

- Generate Video: The painting events are then processed and a video is generated using the cv2 package which simulates the painting activity in a time-lapsed manner.

- Output: The generated video is saved with the format: {date_of_first_event_of_this_day}\_#{day_number}\_{theme}.mp4.

Feel free to modify and expand upon this README to better suit your project's specifics!