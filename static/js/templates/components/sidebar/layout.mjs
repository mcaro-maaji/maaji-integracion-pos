/**
 * @fileoverview Logica del template "templates/components/layout".
 * @module templates/components/layout
 * @author Manuel Caro
 * @version 1.0.0
 */

const toggleBtn = document.getElementById("toggleSidebar")
const sidebar = document.getElementById("sidebar")
const mainContent = document.getElementById("mainContent")

if (sidebar && sidebar.classList.contains("collapsed") && mainContent) {
    mainContent.classList.add("expanded")
} else if (sidebar && mainContent) {
    mainContent.classList.remove("expanded")
}

if (toggleBtn && sidebar && mainContent) {
    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed")
        mainContent.classList.toggle("expanded")
    })
}
