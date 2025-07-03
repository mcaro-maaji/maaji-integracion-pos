/**
 * @fileoverview Contiene el tipado de la API, estructuras.
 * @module api/types
 * @author Manuel Caro
 * @version 1.0.0
 */

declare global {
    export namespace Api {
        /** Respuesta de la API que identifica las operaciones disponibles. */
        export interface DescriptionOperation {
            name: string
            type?: string
            func?: string
            desc?: string
        }

        /** Respuesta de la API que identifica los parametros de las operaciones disponibles. */
        export interface DescriptionParamsOpt extends DescriptionOperation { }

        /** Respuesta de la API que identifica un listado operaciones disponibles. */
        export interface DescriptionOperations {
            operations: DescriptionOperation[]
        }

        /** Respuesta al consultar la informacion de la API, generalmente los parametros. */
        export interface Information {
            parameters?: DescriptionParamsOpt[]
            parameterskv?: Object<string, DescriptionParamsOpt>
            return?: DescriptionParamsOpt
        }
        
        export type JsonValue = string | number | boolean | null | undefined | JsonValue[] | { [key: string]: JsonValue }
        
        /** Parametros esperados por la API. */
        export interface Parameters {
            parameters?: JsonValue[]
            parameterskv?: { [key: string]: JsonValue }
        }

        /** Objecto esperado como resultado despues de correr la API. */
        export interface Result<T extends JsonValue> {
            data: T
            type: string
            errs?: string
        }

        /** Tipo para mapear los argumentos de la funcion Api.run */
        export type ArgumentsKv = { [key: string]: JsonValue }
        export type Arguments = JsonValue[]
    }
}

export { }
