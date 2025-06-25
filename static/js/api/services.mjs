/**
 * @fileoverview Clase principal que mapea y consume la API de la aplicacion del apartado de servicios.
 * @module api/services
 * @author Manuel Caro
 * @version 1.0.0
 */

import { ApiBase } from "./base.mjs"
import { ApiURLServices } from "./url.mjs"
import { API_URL_SERVICES } from "./constants.mjs"

/**
 * @template {Api.JsonValue} T
 * @class
 * @extends ApiBase<T>
 */
export class ApiServices extends ApiBase {
    /**
     * @param {string | URL | ApiURLServices} url 
     */
    constructor(url) {
        super(url, API_URL_SERVICES)
    }
}

export const services = {
    mapFields: {
        clients: {
            /** @type {ApiServices<string>} */
            create: new ApiServices("mapfields/clients/create"),
            /** @type {ApiServices<string[]>} */
            getall: new ApiServices("mapfields/clients/getall"),
            /** @type {ApiServices<[string, string][]>} */
            get: new ApiServices("mapfields/clients/get"),
            /** @type {ApiServices<number>} */
            pop: new ApiServices("mapfields/clients/pop"),
            /** @type {ApiServices<number>} */
            persistent: new ApiServices("mapfields/clients/persistent")
        }
    },
    clients: {
        cegid: {
            /** @type {ApiServices<string>} */
            create: new ApiServices("clients/cegid/create"),
            /** @type {ApiServices<string[]>} */
            getall: new ApiServices("clients/cegid/getall"),
            /** @type {ApiServices<Api.JsonValue[] | string>} */
            get: new ApiServices("clients/cegid/get"),
            /** @type {ApiServices<number>} */
            drop: new ApiServices("clients/cegid/drop"),
            /** @type {ApiServices<number>} */
            pop: new ApiServices("clients/cegid/pop"),
            /** @type {ApiServices<number>} */
            persistent: new ApiServices("clients/cegid/persistent"),
            /** @type {ApiServices<[string, string][]>} */
            requiredFields: new ApiServices("clients/cegid/requiredfields"),
            /** @type {ApiServices<number>} */
            sortFields: new ApiServices("clients/cegid/sortfields"),
            /** @type {ApiServices<number>} */
            fix: new ApiServices("clients/cegid/fix"),
            /** @type {ApiServices<number>} */
            normalize: new ApiServices("clients/cegid/normalize"),
            /** @type {ApiServices<[[string, string], number[]][]>} */
            analysis: new ApiServices("clients/cegid/analysis"),
            /** @type {ApiServices<number>} */
            autoFix: new ApiServices("clients/cegid/autofix"),
            /** @type {ApiServices<[[string, string], number[]][]>} */
            fullFix: new ApiServices("clients/cegid/fullfix"),
            /** @type {ApiServices<(string | null)[]>} */
            exceptions: new ApiServices("clients/cegid/exceptions"),
            /** @type {ApiServices<number>} */
            save: new ApiServices("clients/cegid/save"),
        },
        shopify: {
            /** @type {ApiServices<string>} */
            create: new ApiServices("clients/shopify/create"),
            /** @type {ApiServices<string[]>} */
            getall: new ApiServices("clients/shopify/getall"),
            /** @type {ApiServices<Api.JsonValue[] | string>} */
            get: new ApiServices("clients/shopify/get"),
            /** @type {ApiServices<number>} */
            drop: new ApiServices("clients/shopify/drop"),
            /** @type {ApiServices<number>} */
            pop: new ApiServices("clients/shopify/pop"),
            /** @type {ApiServices<number>} */
            persistent: new ApiServices("clients/shopify/persistent"),
            /** @type {ApiServices<[string, string][]>} */
            requiredFields: new ApiServices("clients/shopify/requiredfields"),
            /** @type {ApiServices<number>} */
            sortFields: new ApiServices("clients/shopify/sortfields"),
            /** @type {ApiServices<number>} */
            fix: new ApiServices("clients/shopify/fix"),
            /** @type {ApiServices<number>} */
            normalize: new ApiServices("clients/shopify/normalize"),
            /** @type {ApiServices<[[string, string], number[]]>} */
            analysis: new ApiServices("clients/shopify/analysis"),
            /** @type {ApiServices<number>} */
            autoFix: new ApiServices("clients/shopify/autofix"),
            /** @type {ApiServices<number>} */
            fullFix: new ApiServices("clients/shopify/fullfix"),
            /** @type {ApiServices<(string | null)[]>} */
            exceptions: new ApiServices("clients/shopify/exceptions"),
            /** @type {ApiServices<number>} */
            save: new ApiServices("clients/shopify/save"),
        }
    }
}

export default services
