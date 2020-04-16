#!/bin/sh

APP_NAME='DynamicPlacementGenerator'

cf set-env $APP_NAME LOGGING_LEVEL	$LOGGING_LEVEL
cf set-env $APP_NAME FIRST_RUN		$FIRST_RUN
