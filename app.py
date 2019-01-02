import logging
import requests
from flask import Flask
from flask_ask import Ask, statement, audio
from datetime import datetime
import calendar

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
API_URL = 'https://api.desiringgod.org/'


@ask.default_intent
@ask.launch
@ask.intent('AMAZON.FallbackIntent')
def launch():
    """
    This method handles Alexa skill play requests
    :return: json for response for Alexa
    """
    # Calculation of page number for DG API, leap year and current date effects index of page
    now = datetime.now()
    is_leap_year = calendar.isleap(now.year)
    if is_leap_year or now < datetime.strptime('02-27-' + str(now.year) + ' 23:59:59.99', '%m-%d-%Y %H:%M:%S.%f'):
        day_of_year = datetime.now().timetuple().tm_yday
    else:
        day_of_year = datetime.now().timetuple().tm_yday + 1
    url = API_URL + '/v0/collections/lojscgpq/resources?page[size]=1&page[number]=' + str(day_of_year)
    try:
        r = requests.get(url, headers={'Authorization': 'Token token="e6f600e7ee34870d05a55b28bc7e4a91"'})
        if r.status_code != 200:
            return statement('I am having trouble playing the devotional. Please try again.')
        data = r.json()
        try:
            sound_url = data['data'][0]['attributes']['audio_stream_url']
            title = data['data'][0]['attributes']['title']

            audio_item = audio('Here is a reading of today\'s solid joys devotional from Desiring God').play(sound_url)
            audio_item._response['directives'][0]['audioItem']['metadata'] = {
                "title": title,
                "subtitle": 'Desiring God',
                "art": {
                  "sources": [
                    {
                      "url": "https://s3.amazonaws.com/alexaskillresourcesabarranc/icon.jpg"
                    }
                  ]
                }
            }
            return audio_item
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
    """
    This method handles Alexa skill unsupported requests
    :return: json for response for Alexa
    """
    return statement('I can\'t do this since its a devotional.')


@ask.intent('AMAZON.PauseIntent')
def stop_audio():
    """
    This method handles Alexa skill pause requests
    :return: json for response for Alexa
    """
    try:
        return audio('Ok, pausing the audio').stop()
    except Exception as err:
        logging.error(err)
        return statement('Nothing to pause.')


@ask.intent('AMAZON.StartOverIntent')
def resume():
    """
    This method handles Alexa skill start over requests
    :return: json for response for Alexa
    """
    try:
        return audio('Starting over.').start_over()
    except Exception as err:
        logging.error(err)
        return statement('Nothing to start over.')


@ask.intent('AMAZON.ResumeIntent')
def resume():
    """
    This method handles Alexa skill resume requests
    :return: json for response for Alexa
    """
    try:
        return audio('Resuming.').resume()
    except Exception as err:
        logging.error(err)
        return statement('Nothing to resume.')


@ask.intent('AMAZON.CancelIntent')
@ask.intent('AMAZON.StopIntent')
def stop():
    """
    This method handles Alexa skill stop and cancel requests
    :return: json for response for Alexa
    """
    try:
        return audio('Stopping').clear_queue(stop=True)
    except Exception as err:
        logging.error(err)
        return statement('Nothing to stop or cancel.')


@ask.on_playback_stopped()
@ask.on_playback_failed()
@ask.on_playback_finished()
@ask.on_playback_nearly_finished()
@ask.on_playback_started()
@ask.session_ended
def return_ok():
    """
    This method handles Alexa skill null requests
    :return: json for response for Alexa
    """
    return '''{
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
        }
    }''', 200


if __name__ == '__main__':
    app.run(debug=True)
