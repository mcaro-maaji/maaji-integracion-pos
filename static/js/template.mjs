/**
 * Almacena contexto de cliente de los templates renderizados.
 * @fileoverview Ejecucion de logica script de los templates de la aplicacion.
 * @module template
 * @author Manuel Caro
 * @version 1.0.0
 */

import { TEMPLATES_URL } from "./utils/constants.mjs"

/** @param {*} context */
export async function default_render(context) {}

const cache_token = "CACHE_TEMPLATES_SCRIPTS"

/** @returns {{ [x: string]: { [x: string]: Api.JsonValue } }} */
function getCacheContext() {
    return JSON.parse(sessionStorage.getItem(cache_token) || "{}")
}

/**
 * @param {URL} url
 * @param {{ [x: string]: Api.JsonValue }} context
 */
function setCacheContext(url, context) {
    const cache = getCacheContext()
    cache[url.href] = context
    sessionStorage.setItem(cache_token, JSON.stringify(cache))
}

/**
 * @class
 */
export class TemplateScript {
    /**
     * @param {string | URL} url
     * @param {{ [x: string]: Api.JsonValue }} [initContext] 
     */
    constructor(url, initContext) {
        if (!(url instanceof URL)) {
            url = new URL(url, TEMPLATES_URL)
        }
        /** @type {URL} */
        this.url = url

        /** @type {{ [x: string]: Api.JsonValue }} */
        this.context = Object()
        if (typeof initContext !== "undefined") {
            this.context = initContext
        } else {
            const cache = getCacheContext()
            if (this.url.href in cache) {
                const context = cache[this.url.href]
                this.context = context
            }
        }
        setCacheContext(this.url, this.context)
    }

    async getRender() {
        let render = default_render
        render = (await import(this.url.href)).default

        if (typeof render !== "function" || render.length !== 1) {
            render = default_render
        }

        return render
    }

    /**
     * @param {{ [x: string]: Api.JsonValue }} [tempContext]
     */
    async exec(tempContext) {
        if (typeof tempContext === "undefined") {
            tempContext = this.context
        }

        let render = default_render

        try {
            render = await this.getRender()
        } catch {
            const err = new Error("Al cargar el script en la URL: " + this.url.href)
            err.name = "TemplateScriptError"
            throw err
        }

        await render(tempContext)
        setCacheContext(this.url, this.context)
    }
}

globalThis.TemplateScript = TemplateScript
export default TemplateScript
