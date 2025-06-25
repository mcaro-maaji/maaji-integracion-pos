/**
 * @fileoverview Contiene el tipado de la API, type guards.
 * @module api/types
 * @author Manuel Caro
 * @version 1.0.0
*/

/**
 * @param {*} obj
 * @returns {obj is Api.DescriptionOperation}
 */
export function isDescriptionOperation(obj) {
    if (typeof obj !== "object" || obj === null) return false;
    const hasName = "name" in obj && typeof obj.name === "string"
    const hasType = ("type" in obj && typeof obj.type === "string") || !("type" in obj)
    const hasFunc = ("func" in obj && typeof obj.func === "string") || !("func" in obj)
    const hasDesc = ("desc" in obj && typeof obj.desc === "string") || !("desc" in obj)

    return hasName && hasType && hasFunc && hasDesc
}

/**
 * @param {*} obj
 * @returns {obj is Api.DescriptionOperations}
 */
export function isDescriptionOperations(obj) {
    if (typeof obj !== "object" || obj === null) return false;
    let hasOperations = "operations" in obj && Array.isArray(obj.operations)
    hasOperations = hasOperations && Array.from(obj.operations).every(isDescriptionOperation)

    return hasOperations
}

/**
 * @type {(obj: any) => obj is Api.DescriptionParamsOpt}
 */
export const isDescriptionParamsOpt = isDescriptionOperation

/**
 * @param {*} obj
 * @returns {obj is Api.Information}
 */
export function isInformation(obj) {
    if (typeof obj !== "object" || obj === null) return false

    let hasParams = "parameters" in obj && Array.isArray(obj.parameters)
    hasParams = hasParams && Array.from(obj.parameters).every(isDescriptionParamsOpt)
    hasParams = hasParams || !("parameters" in obj)

    let hasParamsKv = "parameterskv" in obj && typeof obj.parameterskv === "object"
    hasParamsKv = hasParamsKv && obj.parameterskv !== null
    hasParamsKv = hasParamsKv && !Array.isArray(obj.parameterskv)
    hasParamsKv = hasParamsKv && Object.values(obj.parameterskv).every(isDescriptionParamsOpt)
    hasParamsKv = hasParamsKv || !("parameterskv" in obj)

    let hasReturn = "return" in obj && isDescriptionParamsOpt(obj.return)
    hasReturn = hasReturn || !("return" in obj)

    return hasParams && hasParamsKv && hasReturn
}

/**
 * @param {*} obj
 * @returns {obj is Api.Parameters}
 */
export function isParameters(obj) {
    if (typeof obj !== "object" || obj === null) return false

    try {
        JSON.stringify(obj)
    } catch {
        return false
    }

    let hasParams = "parameters" in obj && Array.isArray(obj.parameters)
    let hasParamsKv = "parameterskv" in obj && typeof obj.parameterskv == "object"
    hasParamsKv = hasParamsKv || obj.parameterskv !== null
    hasParamsKv = hasParamsKv || !Array.isArray(obj.parameterskv)
    hasParamsKv = hasParamsKv || Object.getPrototypeOf(obj.parameterskv) === Object.prototype
    hasParamsKv = hasParamsKv || !("parameterskv" in obj)

    return hasParams && hasParamsKv
}

/**
 * @template {Api.JsonValue} T
 * @param {*} obj
 * @returns {obj is Api.Result<T>}
 */
export function isResult(obj) {
    if (typeof obj !== "object" || obj === null) return false;

    let hasData = "data" in obj && typeof obj.data !== "undefined"
    let hasType = "type" in obj && typeof obj.type === "string"
    let hasErrs = "errs" in obj && typeof obj.errs === "string"
    hasErrs = hasErrs || !("errs" in obj)

    return hasData && hasType && hasErrs
}
