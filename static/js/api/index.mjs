/**
 * @fileoverview Modulo para consumir la API de la aplicacion.
 * @module api/index
 * @author Manuel Caro
 * @version 1.0.0
 */

import * as types from "./types.mjs"
import { ApiError, ApiURLError, ApiParamsError } from "./errors.mjs"
import { ApiURL, ApiURLServices, ApiURLWeb, ApiURLScripts } from "./url.mjs"
import { ApiBase, getErrorApi } from "./base.mjs"
import { ApiServices, services } from "./services.mjs"
import { ApiScripts, scripts } from "./scripts.mjs"
import { ApiWeb, web } from "./web.mjs"

export {
    types,
    ApiError, ApiURLError, ApiParamsError,
    ApiURL, ApiURLServices, ApiURLWeb, ApiURLScripts,
    ApiBase,
    getErrorApi,
    ApiServices,
    ApiScripts,
    ApiWeb
}

export const api = {
    services,
    scripts,
    web
}

export default api
