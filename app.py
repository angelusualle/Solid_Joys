import logging
import requests
from flask import Flask
from flask_ask import Ask, statement, audio
from datetime import datetime

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
API_URL = 'https://api.desiringgod.org/'


@ask.launch
@ask.intent('AMAZON.FallbackIntent')
def launch():
    day_of_year = datetime.now().timetuple().tm_yday
    url = API_URL + '/v0/collections/lojscgpq/resources?page[size]=1&page[number]=' + str(day_of_year + 1)
    try:
        r = requests.get(url, headers={'Authorization': 'Token token="e6f600e7ee34870d05a55b28bc7e4a91"'})
        if r.status_code != 200:
            return statement('I am having trouble playing the devotional. Please try again.').s
        data = r.json()
        try:
            sound_url = data['data'][0]['attributes']['audio_stream_url']
            return audio('Here is a reading of today\'s devotional').play(sound_url)
        except Exception as err:
            logging.error(err)
            logging.error(data)
            return statement('I am having trouble playing the devotional. Please try again.')
    except Exception as err:
        logging.error(err)
        return statement('I am having trouble playing the devotional. Please try again.')


@ask.intent('AMAZON.LoopOffIntent')
@ask.intent('AMAZON.LoopOnIntent')
@ask.intent('AMAZON.NextIntent')
@ask.intent('AMAZON.PreviousIntent')
@ask.intent('AMAZON.RepeatIntent')
@ask.intent('AMAZON.ShuffleOnIntent')
@ask.intent('AMAZON.ShuffleOffIntent')
def unsupported_intent():
    return statement('I can\'t do this in this for a devotional.')


@ask.intent('AMAZON.PauseIntent')
def stop_audio():
    try:
        return audio('Ok, stopping the audio').stop()
    except Exception as err:
        logging.error(err)
        return statement('Nothing to pause.')


@ask.intent('AMAZON.StartOverIntent')
def resume():
    try:
        return audio('Starting over.').start_over()
    except Exception as err:
        logging.error(err)
        return statement('Nothing to start over.')


@ask.intent('AMAZON.ResumeIntent')
def resume():
    try:
        return audio('Resuming.').resume()
    except Exception as err:
        logging.error(err)
        return statement('Nothing to resume.')


@ask.intent('AMAZON.CancelIntent')
@ask.intent('AMAZON.StopIntent')
def stop():
    try:
        return audio('Stopping').clear_queue(stop=True)
    except Exception as err:
        logging.error(err)
        return statement('Nothing to stop or cancel.')


@ask.session_ended
def session_ended():
    return '{}', 200


if __name__ == '__main__':
    app.run(debug=True)
