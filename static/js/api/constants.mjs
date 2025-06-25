/**
 * @fileoverview Constantes para la API.
 * @module utils/constants
 * @author Manuel Caro
 * @version 1.0.0
 */

import { DOCUMENT_URL } from "../utils/constants.mjs"

export const PAYLOAD_WEB_FILES = "payload.web.files"
export const API_URL_SERVICES = new URL(DOCUMENT_URL.origin + "/api/services/")
export const API_URL_WEB = new URL(DOCUMENT_URL.origin + "/api/web/")
export const API_URL_SCRIPTS = new URL(DOCUMENT_URL.origin + "/api/scripts/")
