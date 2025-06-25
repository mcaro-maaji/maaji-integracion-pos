/**
 * @fileoverview Clase principal que mapea y consume la API de la aplicacion del apartado Scripts.
 * @module apis/scripts
 * @author Manuel Caro
 * @version 1.0.0
 */

import { ApiBase } from "./base.mjs"
import { ApiURLScripts } from "./url.mjs"
import { API_URL_SCRIPTS } from "./constants.mjs"

/**
 * @template {Api.JsonValue} T
 * @class
 * @extends ApiBase<T>
 */
export class ApiScripts extends ApiBase {
    /**
     * @param {string | URL | ApiURLScripts} url 
     */
    constructor(url) {
        super(url, API_URL_SCRIPTS)
    }
}

export const scripts = {
    clients: {
        cegid: {
            /** @type {ApiScripts<string>} */
            fromraw: new ApiScripts("clients/cegid/fromraw"),
            /** @type {ApiScripts<string>} */
            frompath: new ApiScripts("clients/cegid/frompath"),
            /** @type {ApiScripts<string>} */
            fromfile: new ApiScripts("clients/cegid/fromfile"),
            /** @type {ApiScripts<string[]>} */
            getall: new ApiScripts("clients/cegid/getall"),
            /** @type {ApiScripts<string>} */
            get: new ApiScripts("clients/cegid/get")
        }
    }
}

export default scripts
