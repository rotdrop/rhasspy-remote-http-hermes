"""Hermes MQTT service for remote Rhasspy server"""
import argparse
import logging
import shlex

import paho.mqtt.client as mqtt

from . import RemoteHermesMqtt

_LOGGER = logging.getLogger(__name__)


def main():
    """Main method."""
    parser = argparse.ArgumentParser(prog="rhasspyremote_http_hermes")
    parser.add_argument(
        "--asr-url",
        help="URL of remote speech to text server (e.g., http://localhost:12101/api/speech-to-text)",
    )
    parser.add_argument(
        "--asr-command", help="Command to execute for ASR (WAV to text)"
    )
    parser.add_argument(
        "--nlu-url",
        help="URL of remote intent recognition server (e.g., http://localhost:12101/api/text-to-intent)",
    )
    parser.add_argument(
        "--nlu-command", help="Command to execute for NLU (text to intent)"
    )
    parser.add_argument(
        "--tts-url",
        help="URL of remote text to speech server (e.g., http://localhost:12101/api/text-to-speech)",
    )
    parser.add_argument(
        "--tts-command", help="Command to execute for TTS (text to WAV)"
    )
    # parser.add_argument(
    #     "--handle-url",
    #     help="URL of remote intent handling server (e.g., http://my-server:port/endpoint",
    # )
    # parser.add_argument(
    #     "--handle-command",
    #     help="Command to execute for intent handling",
    # )
    parser.add_argument(
        "--host", default="localhost", help="MQTT host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=1883, help="MQTT port (default: 1883)"
    )
    parser.add_argument(
        "--siteId",
        action="append",
        help="Hermes siteId(s) to listen for (default: all)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    # Split commands
    if args.asr_command:
        args.asr_command = shlex.split(args.asr_command)

    if args.nlu_command:
        args.nlu_command = shlex.split(args.nlu_command)

    if args.tts_command:
        args.tts_command = shlex.split(args.tts_command)

    try:
        # Listen for messages
        client = mqtt.Client()
        hermes = RemoteHermesMqtt(
            client,
            asr_url=args.asr_url,
            asr_command=args.asr_command,
            nlu_url=args.nlu_url,
            nlu_command=args.nlu_command,
            tts_url=args.tts_url,
            tts_command=args.tts_command,
            siteIds=args.siteId,
        )

        def on_disconnect(client, userdata, flags, rc):
            try:
                # Automatically reconnect
                _LOGGER.info("Disconnected. Trying to reconnect...")
                client.reconnect()
            except Exception:
                logging.exception("on_disconnect")

        # Connect
        client.on_connect = hermes.on_connect
        client.on_disconnect = on_disconnect
        client.on_message = hermes.on_message

        _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
        client.connect(args.host, args.port)

        client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.debug("Shutting down")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
