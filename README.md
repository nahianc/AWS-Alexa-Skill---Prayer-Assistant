# AWS Alexa Skill - Prayer Assistant
Amazon Alexa Skill built in Python to allow Alexa muslim users all over the world quickly and easily find out prayer times.

This Skill uses abdulrcs's Daily Prayer Time API to fetch the current days, as well as tomorrows, prayer times, based on a city or province as a query parameter. This paramater is fetched from the users Alexa device via the ASK (Alexa Skills Kit) SDK. By using the ASK SDK to fetch the device ID and access tokens, we can use these two pieces in conjunction to fetch the device address, as well as timezone, which we can then feed to the API for accurate timings to give to the user. 

Since prayer tiems are specific to timezones, location permissions are required to use this skill, however no user data is stored or distributed.

To use this Skill, the only thing that is required is the Alexa app, Amazon Echo, or some other Alexa-enabled device. All you have to do is start by saying "Alexa open Prayer Assistant", and then you can ask it a question like "What time is Fajr", or "When is the next prayer", or "How long until the next prayer?".

[Amazon Alexa Skills Store listing](https://www.amazon.com/dp/B0B4TY1CFS?ref&ref=cm_sw_em_r_as_dp_5zTgC8qnsdD6T)
