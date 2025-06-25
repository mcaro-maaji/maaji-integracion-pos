/**
 * @fileoverview Clase principal que mapea y consume la API de la aplicacion del apartado ApiWeb.
 * @module api/web
 * @author Manuel Caro
 * @version 1.0.0
 */

import { ApiBase } from "./base.mjs"
import { ApiURLWeb } from "./url.mjs"
import { API_URL_WEB } from "./constants.mjs"

/**
 * @template {Api.JsonValue} T
 * @class
 * @extends ApiBase<T>
 */
export class ApiWeb extends ApiBase {
    /**
     * @param {string | URL | ApiURLWeb} url 
     */
    constructor(url) {
        super(url, API_URL_WEB)
    }
}

export const web = {
    clients: {
        /** @type {ApiWeb<string>} */
        create: new ApiWeb("clients/create"),
        /** @type {ApiWeb<string>} */
        get: new ApiWeb("clients/get"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        clear: new ApiWeb("clients/clear"),
        /** @type {ApiWeb<number>} */
        fullfix: new ApiWeb("clients/fullfix"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        analyze: new ApiWeb("clients/analyze"),
        /** @type {ApiWeb<(string | null)[]>} */
        exceptions: new ApiWeb("clients/exceptions"),
        /** @type {ApiWeb<string | null>} */
        download: new ApiWeb("clients/download"),
    }
}

export default web
