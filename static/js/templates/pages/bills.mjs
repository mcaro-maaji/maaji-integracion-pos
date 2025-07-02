/**
 * @fileoverview Logica del template "templates/pages/bills".
 * @module templates/pages/bills/cegid
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

/** @type {"local" | "dynamicsApi"} */
let datafrom = "local"
const listSupport = ["csv", "excel", "json", "clipboard"]
const tableElementId = "table-bills"
const tableElement = document.getElementById(tableElementId)
const btnUploadElement = document.getElementById("btnupload-bills")
const inputFileElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-file-bills"))
const inputFileNameElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-filename-bills"))
const btnClearElement = document.getElementById("btnclear-bills")
const selectSupportElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-support-bills"))
const selectOrientJsonElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-orientjson-bills"))
const inputSeparadorElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-separator-bills"))
const btnFullFixElement = document.getElementById("btnfullfix-bills")
const logSquareElement = document.getElementById("logsquare-bills")
const btnDownloadElement = document.getElementById("btndownload-bills")
const inputHeaderElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-header-bills"))
const btnDynamicsElement = /** @type {HTMLButtonElement | null} */ (document.getElementById("btndynamics-bills"))
const btnSubmitModalDynamicsElement =/** @type {HTMLButtonElement | null} */ (document.getElementById("btn-submit-modaldynamics"))
const selectDynamicsEnvElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-dynamics-env"))
const selectDynamicsDataAreaElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-dynamics-data-area"))
const inputDynamicsDateStartElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-dynamics-date-start"))
const inputDynamicsDateEndElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-dynamics-date-end"))

/** @param {"visible" | "hidden" | "loading"} state */
export function setStateTable(state="visible") {
    if (
        btnUploadElement &&
        tableElement &&
        btnFullFixElement &&
        btnDownloadElement &&
        btnDynamicsElement
    ) {
        tableElement.hidden = state !== "visible"
        btnUploadElement.hidden = !(state !== "visible")
        btnDynamicsElement.hidden = !(state !== "visible")

        if (state === "visible") {
            tableElement.classList.remove("d-none")
            btnUploadElement.classList.add("d-none")
            btnDynamicsElement.classList.add("d-none")
            btnFullFixElement.classList.remove("disabled")
            btnDownloadElement.classList.remove("disabled")
        } else {
            tableElement.classList.add("d-none")
            btnUploadElement.classList.remove("d-none")
            btnDynamicsElement.classList.remove("d-none")
            btnFullFixElement.classList.add("disabled")
            btnDownloadElement.classList.add("disabled")

            if (state === "loading") {
                btnUploadElement.classList.add("btn-isloading")
                btnDynamicsElement.classList.add("btn-isloading")
            } else {
                btnUploadElement.classList.remove("btn-isloading")
                btnDynamicsElement.classList.remove("btn-isloading")
            }
        }
    }
}

setStateTable("hidden")

const tableOptions = {
    height: "26vmax",
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
 *   fixed: boolean
 *   filename: string | null
 *   support?: string
 *   sep?: string
 *   index?: boolean
 *   orient?: string
 *   excel?: boolean
 *   header?: boolean | null
 *   dynamicsenv?: string
 *   areaid?: string
 *   datestart?: string | null
 *   dateend?: string | null
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
    const header = inputHeaderElement?.checked || null
    const dynamicsenv = selectDynamicsEnvElement?.value || "PROD"
    const areaid = selectDynamicsDataAreaElement?.value || "AM"
    const datestart = inputDynamicsDateStartElement?.value || null
    const dateend = inputDynamicsDateEndElement?.value || null

    if (!listSupport.includes(support)) {
        throw new ApiError("no se ha seleccionado un soporte valido: " + support)
    }

    const parameterskv = { fixed, filename }

    if (datafrom === "local") {
        if (support === "csv") {
            return { ...parameterskv, support, sep, index, header }
        } else if (support === "excel") {
            return { ...parameterskv, support, index, header }
        } else if (support === "json") {
            return { ...parameterskv, support, orient: orientjson }
        } else if (support === "clipboard") {
            if (sep) return { ...parameterskv, support, excel, index, sep, header  }
            return { ...parameterskv, support, excel, index  }
        }

        return { ...parameterskv, support, sep, orient: orientjson, index, excel }
    } else if (datafrom === "dynamicsApi") {
        return { ...parameterskv, dynamicsenv, areaid, datestart, dateend }
    }
    throw new ApiError("error al cargar la informacion: 'datafrom' -> " + datafrom)
}

const loadLastScroll = (function () {
    let lastScrollTop = table?.rowManager?.element?.scrollTop || 0
    let lastScrollLeft = table?.rowManager?.element?.scrollLeft || 0

    return () => {
        const element = table?.rowManager?.element
        if (element === undefined) return
        const scrollTop = element.scrollTop
        const scrollLeft = element.scrollLeft
        element.scrollTop = lastScrollTop
        element.scrollLeft = lastScrollLeft
        lastScrollTop = scrollTop
        lastScrollLeft = scrollLeft
    }
})()

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

/** @param {string} text */
export function parserLogClient(text) {
    text = text.replace(/^\w+Exception/, "Error")
    text = text.replace(/^\w+Warning/, "Warning")

    text = text.replace("en los siguientes indices:", "en las siguientes filas:")
    const match = text.match(/en las siguientes filas:\s\[((\d+),?\s?)+\]/)

    if (match) {
        const indices = match[0]
        let filas = indices.replace(/\d+/g, num => String(Number(num) + 1))
        filas = filas.replace(/[\[\]]/g, "")
        text = text.replace(indices, filas)
    }

    return text
}

export async function getLogBills() {
    const apiRes = await api.web.bills.exceptions.run()
    const result = await apiRes.result
    /** @type {string[]} */
    const initValue = []
    return result.data.reduce((prev, value) => {
        if (value) {
            return [...prev, parserLogClient(value)]
        }
        return prev
    }, initValue)
}

/**
 * @param {(string)[]} messages
 * @param {"new"|"add"|"start"} func
 */
export function setLogSquare(messages, func="new") {
    if (logSquareElement === null) return

    let textHtml = func === "new" ? "" : logSquareElement.innerHTML
    let text = ""
    messages.forEach((value) => {
        let textColor = "text-dark"

        if (value.startsWith("Success")) textColor = "text-success"
        else if (value.startsWith("Error")) textColor = "text-danger"
        else if (value.startsWith("Warning")) textColor = "text-warning-dark"
        else if (value.startsWith("Info")) textColor = "text-info"

        text += `<span class="w-100 my-2 fs-6 ${textColor}">${value}</span>\n`
    })
    if (func === "start") {
        textHtml = text + textHtml
    } else {
        textHtml += text
    }
    logSquareElement.innerHTML = textHtml
}

export async function createData() {
    setStateTable("loading")
    try {
        const parameterskv = getParameterskv()
        if (datafrom === "local") {
            await api.web.bills.create.run([], parameterskv)
        } else if (datafrom === "dynamicsApi") {
            await api.web.bills.fromapi.run([], parameterskv)
        } else {
            throw new ApiError("error al cargar la informacion: 'datafrom' -> " + datafrom)
        }
        const apiRes = await api.web.bills.get.run([], parameterskv)
        const result = await apiRes.result
        setStateTable("visible")
        setDataOnTable(result.data)
        setLogSquare(["Success: datos cargados."])
    } catch (err) {
        setStateTable("hidden")
        setLogSquare([`Error: no se ha podido cargar la informacion, ${err}`])
    }
}

/**
 * @typedef {EventTarget & { files: FileList }} EventTargetFileList
 * @type {(this: HTMLInputElement, event: Event) => Promise<void>}
 */
export async function listenerInputFile(event) {

    const target = /** @type {EventTargetFileList} */ (event.target)

    if (!(
        target !== null &&
        "files" in target &&
        target.files instanceof FileList &&
        target.files.length > 0
    )) {
        setStateTable("hidden")
        return
    }

    const file = target.files[0]
    api.web.bills.create.addFiles(file)

    await createData()

    if (inputFileNameElement) {
        inputFileNameElement.value = file.name
    }

    if (inputFileElement) {
        inputFileElement.value = ""
    }
}

const toggleBtnFix = () => {
    if (btnFullFixElement === null) return stateBtnFix
    if (stateBtnFix === "fixed") {
        btnFullFixElement.textContent = "Original"
        btnFullFixElement.classList.replace("btn-success", "btn-warning")
    } else {
        btnFullFixElement.textContent = "Reparar"
        btnFullFixElement.classList.replace("btn-warning", "btn-success")
    }
    return stateBtnFix
}

if (btnFullFixElement) {
    btnFullFixElement.addEventListener("click", async () => {
        setStateTable("loading")

        try {
            if (stateBtnFix === "original") {
                await api.web.bills.fullfix.run()
                stateBtnFix = "fixed"
            } else {
                stateBtnFix = "original"
            }
            const parameterskv = getParameterskv()
            const apiRes = await api.web.bills.get.run([], parameterskv)
            const result = await apiRes.result
            toggleBtnFix()
            setStateTable("visible")
            loadLastScroll()
            setDataOnTable(result.data)
            loadLastScroll()
            setLogSquare(await getLogBills())
            // Un solo uso de Reparar porque no esta implementado tener una copia del original
            btnFullFixElement.classList.add("disabled")
        } catch (err) {
            setStateTable("hidden")
            setLogSquare(["Error: no se ha logrado obtener la informacion desde la API"])
        }
    })
}

if (btnDownloadElement) {
    btnDownloadElement.addEventListener("click", async () => {
        const oldDatafrom = datafrom
        datafrom = "local"
        const parameterskv = getParameterskv()
        const apiRes = await api.web.bills.download.run([], parameterskv)
        if (parameterskv.support === "clipboard") {
            const result = await apiRes.result
            if (typeof result.data === "string") {
                const match = result.data.match(/code: 0 \| message: '(.+)'/)
                const message = match ? match[1] : "ocurrrio un error al copiar en el portapapeles."
                setLogSquare(["Info: " + message], "start")
            }
        } else {
            try {
                await apiRes.download
                setLogSquare(["Info: se han descargado los datos."], "start")
            } catch (err) {
                setLogSquare(["Error: no se descargo la informacion, " + String(err)], "start")
            }
        }
        datafrom = oldDatafrom
    })
}

if (btnClearElement) {
    btnClearElement.addEventListener("click", async () => {
        setStateTable("loading")
        table.clearData()
        await api.web.bills.clear.run()
        setStateTable("hidden")
        if (logSquareElement) {
            logSquareElement.innerHTML = ""
        }
        stateBtnFix = "original"
        toggleBtnFix()
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
        if (inputHeaderElement && inputSeparadorElement && selectOrientJsonElement) {
            if (support === "json") {
                inputHeaderElement.parentElement?.classList.add("d-none")
                inputHeaderElement.hidden = true
                inputSeparadorElement.parentElement?.classList.add("d-none")
                inputSeparadorElement.hidden = true
                selectOrientJsonElement.parentElement?.classList.remove("d-none")
                selectOrientJsonElement.hidden = false
            } else if (support === "excel") {
                inputHeaderElement.parentElement?.classList.remove("d-none")
                inputHeaderElement.hidden = false
                inputSeparadorElement.parentElement?.classList.add("d-none")
                inputSeparadorElement.hidden = true
                selectOrientJsonElement.parentElement?.classList.add("d-none")
                selectOrientJsonElement.hidden = true
            } else {
                inputHeaderElement.parentElement?.classList.remove("d-none")
                inputHeaderElement.hidden = false
                inputSeparadorElement.parentElement?.classList.remove("d-none")
                inputSeparadorElement.hidden = false
                selectOrientJsonElement.parentElement?.classList.add("d-none")
                selectOrientJsonElement.hidden = true
            }
        }
    })
}

/** @param {*} context */
export function template(context) {
    if (inputFileElement) {
        inputFileElement.addEventListener("change", listenerInputFile)
    }

    if (btnUploadElement && btnDynamicsElement && inputFileElement) {
        btnUploadElement.onclick = async () => {
            datafrom = "local"
            const { support } = getParameterskv()

            if (support === "clipboard") {
                await createData()
            } else {
                inputFileElement.click()
            }
        }
    }

    if (btnSubmitModalDynamicsElement) {
        btnSubmitModalDynamicsElement.onclick = async () => {
            datafrom = "dynamicsApi"
            await createData()
        }
    }

    if (btnClearElement) {
        btnClearElement.click()
    }
}

export default template
