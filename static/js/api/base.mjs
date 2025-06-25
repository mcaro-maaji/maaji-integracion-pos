/**
 * @fileoverview Clase principal que mapea y consume la API de la aplicacion.
 * @module api/base
 * @author Manuel Caro
 * @version 1.0.0
 */

import { ApiURL } from "./url.mjs"
import { ApiError, ApiURLError, ApiParamsError } from "./errors.mjs"
import { isParameters, isResult } from "./types.mjs"
import { PAYLOAD_WEB_FILES } from "./constants.mjs"

/**
 * @template {Api.JsonValue} T
 * @param {Api.Result<T>} result
 * @param {string} [msg]
 * @returns {ApiError}
 */
export function getErrorApi(result, msg) {
    if (typeof msg === "undefined") {
        msg = "ocurrio un error en la API"
    }
    if (typeof result.errs === "string") {
        msg = msg ? msg + ", " + result.errs : result.errs
    }
    const error = new ApiError(msg)
    error.name = result.type
    return error
}

/**
 * @template {Api.JsonValue} T
 * @class
 */
export class ApiResponse {
    /**
     * @param {Response} response
     * @param {Api.JsonValue[]} [parameters]
     * @param {{ [key: string]: Api.JsonValue }} [parameterskv]
     * @param {boolean} strict
     */
    constructor(response, parameters, parameterskv, strict = true) {
        this.response = response
        this.parameters = parameters || []
        this.parameterskv = parameterskv || {}
        this.strict = strict
    }

    get result() {
        return this.response.json().then(result => {
            /** @type {(obj: any) => obj is Api.Result<T>} */
            const isResultApi = isResult

            if (!isResultApi(result)) {
                throw new ApiError("el servicio debe responder con un tipo Json[ServiceResult].")
            }

            if (this.strict && typeof result.errs === "string") {
                throw getErrorApi(result)
            }

            return result
        }).catch(err => {
            if (err instanceof ApiError) throw err
            throw getErrorApi({
                data: null,
                type: "ApiError",
                errs: "la respuesta del servicio debe tener un content-type json."
            })
        })
    }

    get download() {
        const disposition = this.response.headers.get("Content-Disposition")
        let { filename = "sin titulo" } = this.parameterskv

        if (disposition && disposition.includes("filename")) {
            const match = disposition.match(/filename="?([^"]+)"?/)
            if (match) filename = match[1]
        }

        return this.response.blob().then(blob => {
            const url = URL.createObjectURL(blob)
            const a = document.createElement("a")
            a.href = url
            a.download = String(filename)
            document.body.appendChild(a)
            a.click()
            a.remove()
            URL.revokeObjectURL(url)
        }).catch(err => {
            filename = filename === "sin titulo" ? "" : `'${filename}' `
            throw new ApiError(`ha ocurrido un error al descargar el archivo ${filename}, ${err}`)
        })
    }
}


/**
 * @template {Api.JsonValue} T
 * @class
 */
export class ApiBase {
    /**
     * @param {string | URL | ApiURL} url
     * @param {string | URL | ApiURL} [base]
     */
    constructor(url, base) {
        /** @type {ApiURL} */
        this.url = new ApiURL(url, base)
        /** @type {FormData} */
        this.form = new FormData()
    }

    /**
     * Informar al cliente sobre el servicio, generalmente los parametros.
     * @returns {Promise<Api.Information>}
     */
    async info() {
        const isOperation = await this.url.isOperation()
        if (!isOperation) return {}

        const response = await fetch(this.url)
        
        if (response.status !== 200) {
            throw new ApiError("error al leer la informacion de la API.")
        }
        const result = await response.json()
        return result
    }

    /**
     * @param {Api.JsonValue[]} [parameters]
     * @param {{ [key: string]: Api.JsonValue }} [parameterskv]
     * @param {boolean} strict
     */
    async run(parameters, parameterskv, strict = true) {
        const isOperation = await this.url.isOperation()
        if (!isOperation) {
            const msg = `la URL no define una operacion de la API: '${this.url.href}'`
            throw new ApiURLError(msg)
        }

        const obj = {
            parameters: parameters || [],
            parameterskv: parameterskv || {}
        }

        if (!isParameters(obj)) {
            throw new ApiParamsError("los parametros de la API no son validos.")
        }

        this.form.set("payload.parameters", JSON.stringify(obj.parameters))
        this.form.set("payload.parameterskv", JSON.stringify(obj.parameterskv))

        /** @type {RequestInit} */
        const requestInit = { method: "POST", body: this.form }
        /** @type {Response | null} */
        let response = null
        try {
            response = await fetch(this.url, requestInit)
            if (!response.ok) {
                const status = `code: ${response.status} message: '${response.statusText}'`
                throw new ApiError(`se ha respondido con un estado: ${status}`)
            }
        } catch (err) {
            err = err ? ", " + String(err) : ""
            throw new ApiError("error al hacer la peticion al servicio" + err)
        }
        /** @type {ApiResponse<T>} */
        const apiResponse = new ApiResponse(response, parameters, parameterskv, strict)
        return apiResponse
    }

    /**
     * @param {File[]} files
     * @returns {void}
     */
    addFiles(...files) {
        this.form.delete(PAYLOAD_WEB_FILES)
        files.forEach((file) => {
            this.form.append(PAYLOAD_WEB_FILES, file, file.name)
        })
    }
}
