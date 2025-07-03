/**
 * @fileoverview Logica del template "templates/pages/settings".
 * @module templates/pages/settings/cegid
 * @author Manuel Caro
 * @version 1.0.0
 */

import api, { ApiError } from "../../api/index.mjs"
import {
    Tabulator,
    ResizeColumnsModule,
    EditModule,
    HistoryModule,
    SortModule,
    ResponsiveLayoutModule
} from "../../dependencies/tabulator-master-6.3-dist/tabulator_esm.mjs"

/** @type {string | null} */
let keyname = null
const listSupport = ["csv", "excel", "json", "clipboard"]
const tableElementId = "table-settings"
const tableElement = document.getElementById(tableElementId)
const btnUploadElement = document.getElementById("btnupload-settings")
const inputFileNameElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-filename-settings"))
const selectSupportElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-support-settings"))
const selectOrientJsonElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-orientjson-settings"))
const inputSeparadorElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-separator-settings"))
const btnDownloadElement = document.getElementById("btndownload-settings")

/** @param {"visible" | "hidden" | "loading"} state */
export function setStateTable(state="visible") {
    if (btnUploadElement && tableElement && btnDownloadElement) {
        tableElement.hidden = state !== "visible"
        btnUploadElement.hidden = !(state !== "visible")

        if (state === "visible") {
            tableElement.classList.remove("d-none")
            btnUploadElement.classList.add("d-none")
            btnDownloadElement.classList.remove("disabled")
        } else {
            tableElement.classList.add("d-none")
            btnUploadElement.classList.remove("d-none")
            btnDownloadElement.classList.add("disabled")

            if (state === "loading") {
                btnUploadElement.classList.add("btn-isloading")
            } else {
                btnUploadElement.classList.remove("btn-isloading")
            }
        }
    }
}

setStateTable("loading")

const tableOptions = {
    height: "40vmax",
    layout: "fitColumns",
    resizableColumns: true,
    pagination: "local",
    paginationSize: 25,
    history: true
}

Tabulator.registerModule(ResizeColumnsModule)
Tabulator.registerModule(EditModule)
Tabulator.registerModule(HistoryModule)
Tabulator.registerModule(SortModule)
Tabulator.registerModule(ResponsiveLayoutModule)
const table = new Tabulator("#" + tableElementId, tableOptions)

await new Promise((resolve) => {
    table.on("tableBuilt", function () {
        resolve(undefined)
    })
})

/** @type {"original" | "fixed"} */
let stateBtnFix = "original"

/**
 * @returns {{
 *   support: string
 *   fixed: boolean
 *   filename: string | null
 *   sep?: string
 *   index?: boolean
 *   orient?: string
 *   excel?: boolean
 * }}
 */
export function getParameterskv() {
    const fixed = stateBtnFix === "fixed"
    const support = selectSupportElement?.value.toLowerCase() || "csv"
    const sep = inputSeparadorElement?.value === null ? "|" : inputSeparadorElement?.value
    const filename = inputFileNameElement?.value || null
    const orientjson = selectOrientJsonElement?.value || "records"
    const index = false
    const excel = true

    if (!listSupport.includes(support)) {
        throw new ApiError("no se ha seleccionado un soporte valido: " + support)
    }

    const parameterskv = { support, fixed, filename }

    if (support === "csv") {
        return { ...parameterskv, sep, index }
    } else if (support === "excel") {
        return { ...parameterskv, index }
    } else if (support === "json") {
        return { ...parameterskv, orient: orientjson }
    } else if (support === "clipboard") {
        if (sep) return { ...parameterskv, excel, index, sep  }
        return { ...parameterskv, excel, index  }
    }

    return { support, sep, fixed, filename, orient: orientjson, index, excel }
}

/** @param {string[]} fields */
export function setColumnsOnTable(fields, showRowNum=true) {
    if (fields.length === 0) {
        throw new ApiError("no hay columnas para cargar en la tabla: #" + tableElementId)
    }
    /**
     * @typedef {{
     *    title: string
     *    field: string
     *    editor?: string
     * }} ColumnDefinition
     */

        /** @type {ColumnDefinition[]} */
    let definitions = fields.map(field => ({
        field,
        title: field,
        editor: "input",
    }));

    if (showRowNum) {
        definitions.unshift({
            field: "#RowNum#",
            title: "#",
        });
    }

    table.setColumns(definitions); // UNA sola llamada optimizada
}

/** @param {string} jsonString */
export function setDataOnTable(jsonString) {
    /** @type {{ [x: string]: Api.JsonValue }[]} */
    const data = JSON.parse(jsonString)
    
    if (data.length === 0) {
        throw new ApiError("no hay datos para cargar en la tabla: #" + tableElementId)
    }

    const columns = Object.keys(data[0])
    setColumnsOnTable(columns, true)
    const dataWithRowNum = data.map((row, index) => ({ "#RowNum#": index + 1, ...row }))
    table.setData(dataWithRowNum)
}

export async function createData() {
    setStateTable("loading")
    try {
        const parameterskv = getParameterskv()
        const apiRes = await api.web.settings.get.run([keyname], parameterskv)
        const result = await apiRes.result
        setStateTable("visible")
        setDataOnTable(result.data)
    } catch (err) {
        setStateTable("hidden")
    }
}

if (btnDownloadElement) {
    btnDownloadElement.addEventListener("click", async () => {
        const parameterskv = getParameterskv()
        const apiRes = await api.web.settings.download.run([keyname], parameterskv)
        if (parameterskv.support === "clipboard") {
            await apiRes.result
        } else {
            try {
                await apiRes.download
            } catch (err) {}
        }
    })
}

if (selectSupportElement) {
    selectSupportElement.addEventListener("change", function () {
        const support = this.value
        if (!btnDownloadElement || !btnUploadElement) return
        if (support === "clipboard") {
            btnDownloadElement.textContent = "Copiar"
            if (btnUploadElement.lastElementChild) {
                btnUploadElement.lastElementChild.textContent = "Pegar desde Portapapeles"
            }
        } else {
            btnDownloadElement.textContent = "Descargar"
            if (btnUploadElement.lastElementChild) {
                btnUploadElement.lastElementChild.textContent = "Subir Archivo " + support.toUpperCase()
            }
        }
        if (support === "csv" && keyname === "shopify" && inputSeparadorElement) {
            inputSeparadorElement.value = ","
        }

        if (inputSeparadorElement && selectOrientJsonElement) {
            if (support === "json") {
                inputSeparadorElement.parentElement?.classList.add("d-none")
                inputSeparadorElement.hidden = true
                selectOrientJsonElement.parentElement?.classList.remove("d-none")
                selectOrientJsonElement.hidden = false
            } else if (support === "excel") {
                inputSeparadorElement.parentElement?.classList.add("d-none")
                inputSeparadorElement.hidden = true
                selectOrientJsonElement.parentElement?.classList.add("d-none")
                selectOrientJsonElement.hidden = true
            } else {
                inputSeparadorElement.parentElement?.classList.remove("d-none")
                inputSeparadorElement.hidden = false
                selectOrientJsonElement.parentElement?.classList.add("d-none")
                selectOrientJsonElement.hidden = true
            }
        }
    })
}

/** @param {*} context */
export async function template(context) {
    keyname = context?.keyname || null
    await createData()
}

export default template
