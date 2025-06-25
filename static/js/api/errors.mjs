/**
 * @fileoverview Errores de los servicios.
 * @module api/errors
 * @author Manuel Caro
 * @version 1.0.0
 */

/**
 * @class
 * @extends Error
 */
export class ApiError extends Error {
    /**
     * @param {string} [message]
     * @param {ErrorOptions} [options]
     */
    constructor(message, options) {
        super(message, options)
        this.name = "ApiError"
    }
}

/**
 * @class
 * @extends ApiError
 */
export class ApiURLError extends ApiError {
    /**
     * @param {string} [message]
     * @param {ErrorOptions} [options]
     */
    constructor(message, options) {
        super(message, options)
        this.name = "ApiURLError"
    }
}

/**
 * @class
 * @extends ApiError
 */
export class ApiParamsError extends ApiError {
    /**
     * @param {string} [message]
     * @param {ErrorOptions} [options]
     */
    constructor(message, options) {
        super(message, options)
        this.name = "ApiParamsError"
    }
}
