/**
 * @fileoverview Logica del template "templates/pages/login".
 * @module templates/pages/login
 * @author Manuel Caro
 * @version 1.0.0
 */

import api from "../../api/index.mjs"

const loginFormElement = /** @type {HTMLFormElement | null} */ (document.getElementById("login-form"))
const usernameElement = /** @type {HTMLInputElement | null} */ (document.getElementById("username"))
const passwordElement = /** @type {HTMLInputElement | null} */ (document.getElementById("password"))
const logginLogBoxElement = /** @type {HTMLInputElement | null} */ (document.getElementById("login-log"))

if (loginFormElement && usernameElement && passwordElement && logginLogBoxElement) {
    loginFormElement.addEventListener("submit", async (e) => {
        e.preventDefault()
    
        const username = usernameElement.value
        const password = passwordElement.value

        const response = await api.services.app.session.login.run([], { username, password })
        const result = await response.result

        const match = result.data.match(/code:\s*(\d+)\s*\|\s*message:\s*'([^']+)'/)

        if (match) {
            const code = parseInt(match[1])
            const message = match[2]

            if (code === 0) {
                location.href = "/"
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
    })

}
