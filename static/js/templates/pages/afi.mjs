/**
 * @fileoverview Logica del template "templates/pages/afi".
 * @module templates/pages/afi/cegid
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

let systemPOS = "cegid"
let isSetDataTransfers = false
const listSupport = ["csv", "excel", "json", "clipboard"]
const tableElementId = "table-afi"
const tableElement = document.getElementById(tableElementId)
const btnUploadElement = document.getElementById("btnupload-afi")
const inputFileElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-file-afi"))
const inputFileNameElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-filename-afi"))
const btnClearElement = document.getElementById("btnclear-afi")
const selectSupportElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-support-afi"))
const selectOrientJsonElement = /** @type {HTMLSelectElement | null} */ (document.getElementById("select-orientjson-afi"))
const inputSeparadorElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-separator-afi"))
const btnFullFixElement = document.getElementById("btnfullfix-afi")
const logSquareElement = document.getElementById("logsquare-afi")
const btnDownloadElement = document.getElementById("btndownload-afi")
const inputHeaderElement = /** @type {HTMLInputElement | null} */ (document.getElementById("in-header-afi"))
const btnAFITransfersElement = /** @type {HTMLButtonElement | null} */ (document.getElementById("btnafitransfers-afi"))

/** @param {"visible" | "hidden" | "loading"} state */
export function setStateTable(state="visible") {
    if (
        btnUploadElement &&
        tableElement &&
        btnFullFixElement &&
        btnDownloadElement &&
        btnAFITransfersElement
    ) {
        tableElement.hidden = state !== "visible"
        btnUploadElement.hidden = !(state !== "visible")
        btnAFITransfersElement.hidden = !(state !== "visible")

        if (state === "visible") {
            tableElement.classList.remove("d-none")
            btnUploadElement.classList.add("d-none")
            btnAFITransfersElement.classList.add("d-none")
            btnFullFixElement.classList.remove("disabled")
            btnDownloadElement.classList.remove("disabled")
        } else {
            tableElement.classList.add("d-none")
            btnUploadElement.classList.remove("d-none")
            btnAFITransfersElement.classList.remove("d-none")
            btnFullFixElement.classList.add("disabled")
            btnDownloadElement.classList.add("disabled")

            if (state === "loading") {
                btnUploadElement.classList.add("btn-isloading")
                btnAFITransfersElement.classList.add("btn-isloading")
            } else {
                btnUploadElement.classList.remove("btn-isloading")
                btnAFITransfersElement.classList.remove("btn-isloading")
            }
        }
    }
}

setStateTable("hidden")

const tableOptions = {
    height: "26vmax",
    layout: "fitData",
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
 *   pos: string
 *   sep?: string
 *   index?: boolean
 *   orient?: string
 *   excel?: boolean
 *   header?: string | number | boolean | null
 * }}
 */
export function getParameterskv() {
    const pos = systemPOS || "cegid"
    const fixed = stateBtnFix === "fixed"
    const support = selectSupportElement?.value.toLowerCase() || "csv"
    const sep = inputSeparadorElement?.value === null ? "|" : inputSeparadorElement?.value
    const filename = inputFileNameElement?.value || null
    const orientjson = selectOrientJsonElement?.value || "records"
    const index = false
    const excel = true
    const header = inputHeaderElement?.checked || null

    if (!listSupport.includes(support)) {
        throw new ApiError("no se ha seleccionado un soporte valido: " + support)
    }

    const parameterskv = { support, fixed, filename, pos }

    if (support === "csv") {
        return { ...parameterskv, sep, index, header }
    } else if (support === "excel") {
        return { ...parameterskv, index, header }
    } else if (support === "json") {
        return { ...parameterskv, orient: orientjson }
    } else if (support === "clipboard") {
        if (sep) return { ...parameterskv, excel, index, sep, header  }
        return { ...parameterskv, excel, index, header  }
    }

    return { support, sep, fixed, filename, orient: orientjson, pos, index, excel, header }
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
export function parserLogAfi(text) {
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

export async function getLogAfi() {
    const apiRes = await api.web.afi.exceptions.run()
    const result = await apiRes.result
    /** @type {string[]} */
    const initValue = []
    return result.data.reduce((prev, value) => {
        if (value) {
            return [...prev, parserLogAfi(value)]
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
        if (parameterskv?.header) {
            parameterskv.header = 0
        }
        await api.web.afi.create.run([], parameterskv)
        const apiRes = await api.web.afi.get.run([], parameterskv)
        const result = await apiRes.result
        setStateTable("visible")
        setDataOnTable(result.data)
        setLogSquare(["Success: datos cargados."])
    } catch (err) {
        setStateTable("hidden")
        setLogSquare([`Error: no se ha podido cargar la informacion, ${err}`])
    }
}

export async function setTransfers() {
    setStateTable("loading")
    try {
        const parameterskv = getParameterskv()
        if (parameterskv?.header) {
            parameterskv.header = 0
        }
        await api.web.afi.settransfers.run([], parameterskv)
        setLogSquare(["Success: se han cargado los datos de transferencias ZF."])
    } catch (err) {
        setLogSquare([`Error: no se ha podido cargar la informacion, ${err}`])
    }
    setStateTable("hidden")
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
    
    if (isSetDataTransfers) {
        api.web.afi.settransfers.addFiles(file)
        await setTransfers()
    } else {
        api.web.afi.create.addFiles(file)
        await createData()
    }

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
                await api.web.afi.fullfix.run()
                stateBtnFix = "fixed"
            } else {
                stateBtnFix = "original"
            }
            const parameterskv = getParameterskv()
            const apiRes = await api.web.afi.get.run([], parameterskv)
            const result = await apiRes.result
    
            toggleBtnFix()
            setStateTable("visible")
            loadLastScroll()
            setDataOnTable(result.data)
            loadLastScroll()
            setLogSquare(await getLogAfi())
        } catch (err) {
            setStateTable("hidden")
            setLogSquare(["Error: no se ha logrado obtener la informacion desde la API"])
        }
    })
}

if (btnDownloadElement) {
    btnDownloadElement.addEventListener("click", async () => {
        const parameterskv = getParameterskv()
        const apiRes = await api.web.afi.download.run([], parameterskv)
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
    })
}

if (btnClearElement) {
    btnClearElement.addEventListener("click", async () => {
        setStateTable("loading")
        table.clearData()
        await api.web.afi.clear.run()
        setStateTable("hidden")
        if (logSquareElement) {
            logSquareElement.innerHTML = ""
        }
        stateBtnFix = "original"
        toggleBtnFix()
        if (
            selectSupportElement && selectSupportElement.value === "csv" &&
            systemPOS === "shopify" && inputSeparadorElement
        ) {
            inputSeparadorElement.value = ","
        }
    })
}

if (selectSupportElement) {
    selectSupportElement.addEventListener("change", function () {
        const support = this.value
        if (!btnDownloadElement || !btnUploadElement || !btnAFITransfersElement) return
        if (support === "clipboard") {
            btnDownloadElement.textContent = "Copiar"
            if (btnUploadElement.lastElementChild) {
                btnUploadElement.lastElementChild.textContent = "Pegar desde Portapapeles"
            }
            if (btnAFITransfersElement.lastElementChild) {
                btnAFITransfersElement.lastElementChild.textContent = "Pegar desde Portapapeles"
            }
        } else {
            btnDownloadElement.textContent = "Descargar"
            if (btnUploadElement.lastElementChild) {
                btnUploadElement.lastElementChild.textContent = "Subir Archivo " + support.toUpperCase()
            }
            if (btnAFITransfersElement.lastElementChild) {
                btnAFITransfersElement.lastElementChild.textContent = "Subir Archivo " + support.toUpperCase()
            }
        }
        if (support === "csv" && systemPOS === "shopify" && inputSeparadorElement) {
            inputSeparadorElement.value = ","
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

if (btnUploadElement && btnAFITransfersElement && inputFileElement) {
    btnUploadElement.onclick = async () => {
        isSetDataTransfers = false
        const { support } = getParameterskv()

        if (support === "clipboard") {
            await createData()
        } else {
            inputFileElement.click()
        }
    }

    btnAFITransfersElement.onclick = async () => {
        isSetDataTransfers = true
        const { support } = getParameterskv()

        if (support === "clipboard") {
            await setTransfers()
        } else {
            inputFileElement.click()
        }
    }
}

/** @param {*} context */
export function template(context) {
    systemPOS = "pos" in context ? context.pos : "cegid"

    if (inputFileElement) {
        inputFileElement.addEventListener("change", listenerInputFile)
    }

    if (btnClearElement) {
        btnClearElement.click()
    }
}

export default template
