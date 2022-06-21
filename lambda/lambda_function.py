# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import requests
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import get_api_access_token

from ask_sdk_model import Response
from ask_sdk_model.services import ServiceException
from ask_sdk_model.ui import AskForPermissionsConsentCard

from datetime import datetime, date
from pytz import timezone

# =========================================================================================================================================
NOTIFY_MISSING_PERMISSIONS = 'This skill requires location permissions so we can give you accurate timing. Please enable Location permissions in the Amazon Alexa app.'
NO_ADDRESS = 'It looks like you don\'t have an address set. You can set your address from the companion app.'
LOCATION_FAILURE = 'There was an error with the Device Address API.'
# =========================================================================================================================================
PERMISSIONS = ['read::alexa:device:all:address']
# =========================================================================================================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Salam alaikum, I am your prayer assistant. How can I help you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class PrayerTimeRequestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("PrayerTimeRequestIntent")(handler_input)

    def handle(self, handler_input):
        # get device id
        sys_object = handler_input.request_envelope.context.system
        device_id = sys_object.device.device_id

        # get Alexa Settings API information
        ask_api_endpoint = sys_object.api_endpoint
        ask_api_access_token = sys_object.api_access_token

        # construct systems api location url
        url = f"{ask_api_endpoint}/v1/devices/{device_id}/settings/address"
        headers = {'Authorization': 'Bearer ' + ask_api_access_token}

        try:
            r = requests.get(url, headers=headers)
            res = r.json()
            logger.info("Device API result: {}".format(str(res)))
            user_location = res["stateOrRegion"]
        except Exception:
            return (
                handler_input.response_builder
                    .speak(NOTIFY_MISSING_PERMISSIONS)
                    .set_card(AskForPermissionsConsentCard(permissions=PERMISSIONS))
                    .response
            )

        if user_location is None:
            return (
                handler_input.response_builder
                    .speak(NO_ADDRESS)
                    .response
            )

        api_base_url = "https://dailyprayer.abdulrcs.repl.co/api/"
        api_query = user_location
        endpoint = f"{api_base_url}{api_query}" 
        api_response = requests.get(endpoint)
        if api_response.status_code in range(200, 299):
            todaysPrayerTimes = api_response.json().get("today")

        slots = handler_input.request_envelope.request.intent.slots
        userRequest = slots["prayer"].value
        userRequest_Response = ""

        if(userRequest.lower() == "fajr"):
            userRequest_Response = todaysPrayerTimes.get("Fajr")
        elif(userRequest.lower() == "dhuhr"):
            userRequest_Response = todaysPrayerTimes.get("Dhuhr")
        elif(userRequest.lower() == "asr"):
            userRequest_Response = todaysPrayerTimes.get("Asr")
        elif(userRequest.lower() == "maghrib"):
            userRequest_Response = todaysPrayerTimes.get("Maghrib")
        elif(userRequest.lower() == "isha"):
            userRequest_Response = todaysPrayerTimes.get("Isha'a")

        delimited = userRequest_Response.split(":")
        if(int(delimited[0]) < 12):
            userRequest_Response += " AM"
        else:
            userRequest_Response = str((int(delimited[0])) - 12) + ":" + delimited[1] + " PM"

        speak_output = f"{userRequest} salah is at {userRequest_Response}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class NextPrayerRequestIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NextPrayerRequestIntent")(handler_input)

    def handle(self, handler_input):
        # get device id
        sys_object = handler_input.request_envelope.context.system
        device_id = sys_object.device.device_id

        # get Alexa Settings API information
        ask_api_endpoint = sys_object.api_endpoint
        ask_api_access_token = sys_object.api_access_token

        # construct systems api location url
        address_url = f"{ask_api_endpoint}/v1/devices/{device_id}/settings/address"

        # construct systems api timezone url
        timezone_url = f"{ask_api_endpoint}/v2/devices/{device_id}/settings/System.timeZone"

        headers = {'Authorization': 'Bearer ' + ask_api_access_token}

        try:
            # Obtain user timezone data 
            r = requests.get(timezone_url, headers=headers)
            res = r.json()
            logger.info("Device API result: {}".format(str(res)))
            userTimeZone = res
            # Obtain user location data
            r = requests.get(address_url, headers=headers)
            res = r.json()
            logger.info("Device API result: {}".format(str(res)))
            user_location = res["stateOrRegion"]
        except Exception:
            return (
                handler_input.response_builder
                    .speak(NOTIFY_MISSING_PERMISSIONS)
                    .set_card(AskForPermissionsConsentCard(permissions=PERMISSIONS))
                    .response
            )

#            handler_input.response_builder.speak("There was a problem connecting to location services")
#            return handler_input.response_builder.response

        if user_location is None:
            return (
                handler_input.response_builder
                    .speak(NO_ADDRESS)
                    .response
            )

        api_base_url = "https://dailyprayer.abdulrcs.repl.co/api/"
        api_query = user_location       
        endpoint = f"{api_base_url}{api_query}" 
        api_response = requests.get(endpoint)
        if api_response.status_code in range(200, 299):
            todaysPrayerTimes = api_response.json().get("today")

        now = datetime.now(timezone(userTimeZone)).time().strftime("%H:%M")
        currTime = datetime.strptime(now, '%H:%M').time()

        if(currTime < datetime.strptime(todaysPrayerTimes.get("Fajr"), '%H:%M').time()):
            nextPrayer = "Fajr"
            nextPrayer_Time = todaysPrayerTimes.get("Fajr")
        elif(currTime < datetime.strptime(todaysPrayerTimes.get("Dhuhr"), '%H:%M').time()):
            nextPrayer = "Dhuhr"
            nextPrayer_Time = todaysPrayerTimes.get("Dhuhr")
        elif(currTime < datetime.strptime(todaysPrayerTimes.get("Asr"), '%H:%M').time()):
            nextPrayer = "Asr"
            nextPrayer_Time = todaysPrayerTimes.get("Asr")
        elif(currTime < datetime.strptime(todaysPrayerTimes.get("Maghrib"), '%H:%M').time()):
            nextPrayer = "Maghrib"
            nextPrayer_Time = todaysPrayerTimes.get("Maghrib")
        elif(currTime < datetime.strptime(todaysPrayerTimes.get("Isha'a"), '%H:%M').time()):
            nextPrayer = "Isha"
            nextPrayer_Time = todaysPrayerTimes.get("Isha'a")
        else:
            nextPrayer = "Fajr"
            nextPrayer_Time = api_response.json().get("tomorrow").get("Fajr")

        remainingTimeDelta = datetime.combine(date.min, datetime.strptime(nextPrayer_Time, '%H:%M').time()) - datetime.combine(date.min, currTime)
        remainingHours = remainingTimeDelta.seconds // 3600
        remainingMinutes = remainingTimeDelta.seconds // 60 % 60
        
        delimited = nextPrayer_Time.split(":")
        if( int(delimited[0]) < 12):
            nextPrayer_Time += " AM"
        else:
            nextPrayer_Time = str((int(delimited[0])) - 12) + ":" + delimited[1] + " PM"

        speak_output = f"The next salah is in {remainingHours} hours and {remainingMinutes} minutes, which is {nextPrayer} at {nextPrayer_Time}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can ask for the time of the next prayer, or a specific salah. How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure how to help with that. You can ask for the time of the next prayer, or a specific salah. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """
    The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """
    Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PrayerTimeRequestIntentHandler())
sb.add_request_handler(NextPrayerRequestIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()