# Copyright 2020 Dragonchain, Inc.
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#      6. Trademarks. This License does not grant permission to use the trade
#         names, trademarks, service marks, or product names of the Licensor
#         and its affiliates, except as required to comply with Section 4(c) of
#         the License and to reproduce the content of the NOTICE file.
# You may obtain a copy of the Apache License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.

import json
from typing import Tuple, Dict, Any

from werkzeug import exceptions as werkzeug_exceptions

from webserver.dragonchain import logger
from webserver.dragonchain import exceptions

_log = logger.get_logger()


def get_exception_message(exception: Exception) -> str:
    if len(exception.args) > 0:
        return str(exception.args[0])
    return ""


def flask_http_response(status: int, data: Any) -> Tuple[str, int, Dict[str, str]]:
    """Create a tuple for flask to return
    Args:
        status: integer http status to use
        data: json dumpable data for the return body
    """
    return json.dumps(data, separators=(",", ":")), status, {"Content-Type": "application/json"}


def format_success(msg: Any) -> Dict[str, Any]:
    """Success formatter"""
    return {"success": msg}


def format_error(category: str, msg: str) -> Dict[str, dict]:
    """Format an error in a standard way
    Args:
        category: the type of error
        msg: the message with the error
    """
    return {"error": {"type": category, "details": msg}}


""" Static error messages """


METHOD_NOT_ALLOWED = format_error("METHOD_NOT_ALLOWED", "The method is not allowed for the requested URL.")
CONTRACT_CONFLICT = format_error("CONTRACT_CONFLICT", "Contract or transaction type already exists.")
BAD_STATE = format_error("BAD_STATE", "The action attempted could not be completed because the contract is in an invalid starting state.")
OPENFAAS_ERROR = format_error("OPENFAAS_ERROR", "Internal system error. Please try again later.")
ACTION_FORBIDDEN = format_error("ACTION_FORBIDDEN", "This action is currently disabled.")
NOT_FOUND = format_error("NOT_FOUND", "The requested resource(s) cannot be found.")
ROUTE_NOT_FOUND = format_error("NOT_FOUND", "The requested route was not found.")
BAD_DOCKER_AUTH_ERROR = format_error("BAD_DOCKER_AUTH_ERROR", "The provided docker registry auth cannot be used")
INVALID_NODE_LEVEL = format_error("INVALID_NODE_LEVEL", "Please specify a valid node level (2-5)")
TRANSACTION_TYPE_CONFLICT = format_error("TRANSACTION_TYPE_CONFLICT", "The transaction type you are trying to register already exists")
INTERCHAIN_CONFLICT = format_error("INTERCHAIN_CONFLICT", "An interchain network with the name you provided already exists")
INSUFFICIENT_CRYPTO = format_error("INSUFFICIENT_CRYPTO", "You do not have enough UTXOs or funds in this address to sign a transaction with")
NOT_ACCEPTING_VERIFICATIONS = format_error("NOT_ACCEPTING_VERIFICATIONS", "Not currently accepting verifications")
INVALID_TRANSACTION_TYPE = format_error(
    "INVALID_TRANSACTION_TYPE", "The transaction type you are attempting to use either does not exist or is invalid."
)
ACTION_FORBIDDEN_LAB_CHAIN = format_error(
    "ACTION_FORBIDDEN_LAB_CHAIN",
    "This feature is disabled for Labs. If you are interested in this feature, please visit https://dragonchain.com/pricing",
)
INTERNAL_SERVER_ERROR = format_error("INTERNAL_SERVER_ERROR", "Unexpected error occurred")


""" Dynamic error messages """


def action_forbidden(exception: Exception) -> dict:
    message = get_exception_message(exception)
    return format_error("ACTION_FORBIDDEN", message)


def invalid_auth(exception: Exception) -> dict:
    message = get_exception_message(exception)
    return format_error("AUTHENTICATION_ERROR", message)


def too_many_requests(exception: Exception) -> dict:
    message = get_exception_message(exception)
    return format_error("TOO_MANY_REQUESTS", message)


def contract_limit_exceeded(exception: Exception) -> dict:
    parameter = get_exception_message(exception)
    return format_error(
        "CONTRACT_LIMIT_EXCEEDED",
        f"This chain has exceeded the limit of {parameter} contracts. Please delete contracts before attempting to create more.",
    )


def validation_exception(exception: Exception) -> dict:
    message = get_exception_message(exception)
    return format_error("VALIDATION_ERROR", message)


def bad_request(exception: Exception) -> dict:
    message = get_exception_message(exception)
    return format_error("BAD_REQUEST", message)


def webserver_error_handler(exception: Exception) -> Tuple[str, int, Dict[str, str]]:  # noqa C901
    if isinstance(exception, exceptions.UnauthorizedException):
        status_code = 401
        surface_error = invalid_auth(exception)
    elif isinstance(exception, exceptions.APIRateLimitException):
        status_code = 429
        surface_error = too_many_requests(exception)
    elif isinstance(exception, exceptions.NotFound):
        status_code = 404
        surface_error = NOT_FOUND
    elif isinstance(exception, exceptions.ValidationException):
        status_code = 400
        surface_error = validation_exception(exception)
    elif isinstance(exception, exceptions.BadRequest):
        status_code = 400
        surface_error = bad_request(exception)
    elif isinstance(exception, exceptions.ActionForbidden):
        status_code = 403
        surface_error = action_forbidden(exception)
    elif isinstance(exception, exceptions.NotEnoughCrypto):
        status_code = 400
        surface_error = INSUFFICIENT_CRYPTO
    elif isinstance(exception, exceptions.ContractConflict):
        status_code = 409
        surface_error = CONTRACT_CONFLICT
    elif isinstance(exception, exceptions.TransactionTypeConflict):
        status_code = 409
        surface_error = TRANSACTION_TYPE_CONFLICT
    elif isinstance(exception, exceptions.InterchainConflict):
        status_code = 409
        surface_error = INTERCHAIN_CONFLICT
    elif isinstance(exception, exceptions.InvalidTransactionType):
        status_code = 400
        surface_error = INVALID_TRANSACTION_TYPE
    elif isinstance(exception, exceptions.ContractLimitExceeded):
        status_code = 403
        surface_error = contract_limit_exceeded(exception)
    elif isinstance(exception, exceptions.BadStateError):
        status_code = 400
        surface_error = BAD_STATE
    elif isinstance(exception, exceptions.InvalidNodeLevel):
        status_code = 400
        surface_error = INVALID_NODE_LEVEL
    elif isinstance(exception, exceptions.NotAcceptingVerifications):
        status_code = 412
        surface_error = NOT_ACCEPTING_VERIFICATIONS
    elif isinstance(exception, exceptions.BadDockerAuth):
        status_code = 400
        surface_error = BAD_DOCKER_AUTH_ERROR
    elif isinstance(exception, exceptions.LabChainForbiddenException):
        status_code = 403
        surface_error = ACTION_FORBIDDEN_LAB_CHAIN
    elif isinstance(exception, werkzeug_exceptions.MethodNotAllowed):
        status_code = 405
        surface_error = METHOD_NOT_ALLOWED
    elif isinstance(exception, werkzeug_exceptions.NotFound):
        status_code = 404
        surface_error = ROUTE_NOT_FOUND
    elif isinstance(exception, exceptions.OpenFaasException):
        status_code = 500
        surface_error = OPENFAAS_ERROR
    else:
        status_code = 500
        surface_error = INTERNAL_SERVER_ERROR

    _log.error(f"Responding: {status_code} {surface_error}")

    if status_code >= 500:
        try:
            message = get_exception_message(exception)
            _log.exception(message)
        except Exception:
            _log.exception("Exception while attempting to report error")
    else:  # Exception didn't get logged in report_exception
        _log.exception("Error:")

    return flask_http_response(status_code, surface_error)
