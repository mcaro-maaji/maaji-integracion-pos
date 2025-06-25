/**
 * @fileoverview Maneja las URL de los servicios.
 * @module Api/url
 * @author Manuel Caro
 * @version 1.0.0
 */

import { ApiURLError } from "./errors.mjs"
import { isDescriptionOperations } from "./types.mjs"
import { API_URL_SERVICES, API_URL_WEB, API_URL_SCRIPTS } from "./constants.mjs"

/**
 * @class
 * @extends URL
 */
export class ApiURL extends URL {
    /**
     * @param {string | URL} url 
     * @param {string | URL} [base]
     */
    constructor(url, base) {
        if (typeof base === "undefined") {
            base = API_URL_SERVICES
        }
        if (typeof base === "string") {
            base = new URL(base)
        }
        super(url, base)
        let err = ""

        if (this.origin !== base.origin) {
            err = "el origen de la url API debe ser el mismo que del documento."
        }
        if (!this.pathname.startsWith(base.pathname)) {
            err = "la URL de la API no es valida: " + this.href
        }
        if (err !== "") {
            throw new ApiURLError(err)
        }
    }

    /**
     * @returns {Promise<boolean>}
     */
    async isOperation() {
        const pathname = this.pathname.split("/")
        const nameOperation = pathname.at(-1) || ""
        const urlOperations = new URL(this.origin + "/" + pathname.slice(0, -1).join("/"))
        const response = await fetch(urlOperations)
        const result = await response.json()
        if (response.status !== 200 || !isDescriptionOperations(result)) return false
        return result.operations.some((descOpt) => descOpt.name === nameOperation)
    }
}

/**
 * @class
 * @extends ApiURL
 */
export class ApiURLServices extends ApiURL {
    /**
     * @param {string | URL} url 
     * @param {string | URL} [base]
     */
    constructor(url, base) {
        if (typeof base === "undefined") {
            base = API_URL_SERVICES
        }
        super(url, base)
    }
}

/**
 * @class
 * @extends ApiURL
 */
export class ApiURLWeb extends ApiURL {
    /**
     * @param {string | URL} url 
     * @param {string | URL} [base]
     */
    constructor(url, base) {
        if (typeof base === "undefined") {
            base = API_URL_WEB
        }
        super(url, base)
    }
}

/**
 * @class
 * @extends ApiURL
 */
export class ApiURLScripts extends ApiURL {
    /**
     * @param {string | URL} url 
     * @param {string | URL} [base]
     */
    constructor(url, base) {
        if (typeof base === "undefined") {
            base = API_URL_SCRIPTS
        }
        super(url, base)
    }
}
