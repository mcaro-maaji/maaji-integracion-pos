/**
 * @fileoverview Logica del template "templates/pages/home".
 * @module templates/pages/home
 * @author Manuel Caro
 * @version 1.0.0
 */

/** @param {{ data: number }} context */
export function renderTemplate(context) {
    // Test render
    if (typeof context.data === "undefined") {
        context.data = 0
    }
    context.data = context.data + 100
}

export default renderTemplate
