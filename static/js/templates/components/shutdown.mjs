/**
 * @fileoverview Logica del template "templates/component/shutdown".
 * @module templates/component/shutdown
 * @author Manuel Caro
 * @version 1.0.0
 */

import api from "../../api/index.mjs"

/** @param {*} context */
export function template(context) {
    const shutDownButton = /** @type {HTMLInputElement | null} */ (document.getElementById("btn-shutdown"))
    const logginLogBoxElement = /** @type {HTMLInputElement | null} */ (document.getElementById("login-log"))

    if (shutDownButton) {
        shutDownButton.addEventListener("click", async () => {
            const response = await api.services.app.commands.shutdown.run()

            if (logginLogBoxElement) {
                const result = await response.result
                const match = result.data.match(/code:\s*(\d+)\s*\|\s*message:\s*'([^']+)'/)
        
                if (match) {
                    const code = parseInt(match[1])
                    const message = match[2]

                    if (code === 0) {
                        location.href = "/";
                        logginLogBoxElement.textContent = message
                        logginLogBoxElement.classList.remove("d-none")
                        logginLogBoxElement.classList.remove("alert-danger")
                        logginLogBoxElement.classList.add("alert-success")
                    } else {
                        logginLogBoxElement.textContent = message
                        logginLogBoxElement.classList.remove("d-none")
                        logginLogBoxElement.classList.remove("alert-success")
                        logginLogBoxElement.classList.add("alert-danger")
                    }
                } else {
                    logginLogBoxElement.textContent = "no se tuvo respuesta del servicio."
                    logginLogBoxElement.classList.remove("d-none")
                    logginLogBoxElement.classList.remove("alert-success")
                    logginLogBoxElement.classList.add("alert-danger")
                }
            }
        })
    }
}

export default template
