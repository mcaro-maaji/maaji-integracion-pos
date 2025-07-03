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
    },
    afi: {
        /** @type {ApiWeb<string>} */
        create: new ApiWeb("afi/create"),
        /** @type {ApiWeb<string>} */
        settransfers: new ApiWeb("afi/settransfers"),
        /** @type {ApiWeb<string>} */
        get: new ApiWeb("afi/get"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        clear: new ApiWeb("afi/clear"),
        /** @type {ApiWeb<number>} */
        fullfix: new ApiWeb("afi/fullfix"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        analyze: new ApiWeb("afi/analyze"),
        /** @type {ApiWeb<(string | null)[]>} */
        exceptions: new ApiWeb("afi/exceptions"),
        /** @type {ApiWeb<string | null>} */
        download: new ApiWeb("afi/download"),
    },
    bills: {
        /** @type {ApiWeb<string>} */
        create: new ApiWeb("bills/create"),
        /** @type {ApiWeb<string>} */
        fromapi: new ApiWeb("bills/fromapi"),
        /** @type {ApiWeb<string>} */
        get: new ApiWeb("bills/get"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        clear: new ApiWeb("bills/clear"),
        /** @type {ApiWeb<number>} */
        fullfix: new ApiWeb("bills/fullfix"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        analyze: new ApiWeb("bills/analyze"),
        /** @type {ApiWeb<(string | null)[]>} */
        exceptions: new ApiWeb("bills/exceptions"),
        /** @type {ApiWeb<string | null>} */
        download: new ApiWeb("bills/download"),
    },
    products: {
        /** @type {ApiWeb<string>} */
        create: new ApiWeb("products/create"),
        /** @type {ApiWeb<string>} */
        fromapi: new ApiWeb("products/fromapi"),
        /** @type {ApiWeb<string>} */
        get: new ApiWeb("products/get"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        clear: new ApiWeb("products/clear"),
        /** @type {ApiWeb<number>} */
        fullfix: new ApiWeb("products/fullfix"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        analyze: new ApiWeb("products/analyze"),
        /** @type {ApiWeb<(string | null)[]>} */
        exceptions: new ApiWeb("products/exceptions"),
        /** @type {ApiWeb<string | null>} */
        download: new ApiWeb("products/download"),
    },
    prices: {
        /** @type {ApiWeb<string>} */
        create: new ApiWeb("prices/create"),
        /** @type {ApiWeb<string>} */
        fromapi: new ApiWeb("prices/fromapi"),
        /** @type {ApiWeb<string>} */
        get: new ApiWeb("prices/get"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        clear: new ApiWeb("prices/clear"),
        /** @type {ApiWeb<number>} */
        fullfix: new ApiWeb("prices/fullfix"),
        /** @type {ApiWeb<[[string, string], number[]][]>} */
        analyze: new ApiWeb("prices/analyze"),
        /** @type {ApiWeb<(string | null)[]>} */
        exceptions: new ApiWeb("prices/exceptions"),
        /** @type {ApiWeb<string | null>} */
        download: new ApiWeb("prices/download"),
    },
    settings: {
        /** @type {ApiWeb<string>} */
        get: new ApiWeb("settings/get"),
        /** @type {ApiWeb<string | null>} */
        download: new ApiWeb("settings/download"),
    }
}

export default web
