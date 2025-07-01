"""Modulo para la definicion de los campos de la funcionalidad de productos."""

from typing import TypedDict, TypeGuard
from enum import StrEnum

class ProductField(StrEnum):
    """Nombre de las columnas de las productos de la api Dynamics 365."""
    ID_INTEGRACION = "CodigCegidArticulos"
    SKU = "referenciaProducto"
    REFERENCIA = "codigoAlternoProducto"
    NOMBRE = "nombreLargoProducto"
    NOMBRE_CORTO = "nombreCortoProducto"
    EAN = "codigoBarrasProducto"
    PROVEEDOR = "proveedorPrincipal"
    MASCARA_DIMENSION = "mascaraDimension"
    DIMENSION = "dimension"
    TALLA = "codigoAlternoTalla"
    NOMBRE_TALLA = "nombre1Talla"
    DIMENSION_2 = "dimension2"
    COLOR = "codigoAlternoColor"
    NOMBRE_COLOR = "nombre1Color"
    TEMPORADA = "codigoAlternoTemporada"
    NOMBRE_TEMPORADA = "nombreTemporada"
    CODIGO_GRUPO = "cod_grupo"
    GRUPO = "grupo"
    CODIGO_LINEA_SECCION = "lineaseccion_COD"
    NOMBRE_LINEA_SECCION = "lineaseccion_NOMBRE"
    CATEGORIA = "codigoAlterno1Categoria"
    DESCRIPCION_CATEGORIA = "DescAlterno1Categoria"
    CATEGORIA_2 = "codigoAlterno2Categoria"
    DECRIPTCION_CATEGORIA_2 = "DescAlterno2Categoria"
    CATEGORIA_3 = "codigoAlterno3Categoria"
    DESCRIPCION_CATEGORIA_3 = "DescAlterno3Categoria"
    CATEGORIA_4 = "codigoAlterno4Categoria"
    DECRIPTCION_CATEGORIA_4 = "DescAlterno4Categoria"
    CODIGO_CLIENTE_OBJETIVO = "codClienteObjetivo"
    DESCRIPCION_CLIENTE_OBJETIVO = "desClienteObjetivo"
    TIPO_NEGOCIO = "codigoAlternoTipoNegocio"
    NOMBRE_TIPO_NEGOCIO = "nombreTipoNegocio"
    MARCA = "codigoAlternoMarca"
    NOMBRE_MARCA = "nombreMarca"
    CODIGO_EVENTO = "codEvento"
    DESCRIPCION_EVENTO = "desEvento"
    PAIS = "codigoAlternoPais"
    NOMBRE_PAIS = "nombrePais"
    TIPO_PRODUCTO = "codigoAlternoTipoProducto"
    NOMBRE_TIPO_PRODUCTO = "nombreTipoProducto"
    FAMILIA_TASA1_ARTICULO = "familiaTasa1Articulo"
    PRECIO_INPUESTO_INC = "precioDetalleImpuestoIncl"
    ESTADO_PRODUCTO = "estadoProducto"
    ESTADO_CONSERVACION = "estadoConservacion"
    FECHA_CREACION_PRODUCTO = "fechaCreacionProducto"
    CONCEPTO_PRODUCTO = "conceptoProducto"
    CODIGO_DIFUSION = "codDIFUSION"
    DESCRIPCION_DIFUSION = "DescDIFUSION"
    CODIGO_ESTRATEGIA = "codESTRATEGIA"
    DESCRIPCION_ESTRATEGIA = "descESTRATEGIA"
    FECHA_INICIO_EVENTO = "fechaInicioEvento"
    FECHA_FIN_EVENTO = "fechaFinEvento"
    NOMBRE_TALLA_2 = "nombre2Talla"
    NOMBRE_TALLA_3 = "nombre3Talla"
    TALLA_COMPLEMENTO = "codigoAlternoTallaComplemento"
    NOMBRE_TALLA_COMPLEMENTO_1 = "nombre1TallaComplemento"
    NOMBRE_TALLA_COMPLEMENTO_2 = "nombre2TallaComplemento"
    NOMBRE_TALLA_COMPLEMENTO_3 = "nombre3TallaComplemento"
    NOMBRE_COLOR_2 = "nombre2Color"
    CALIFICACION_ESTADO_CONSERVACION = "calificacionEstadoConservacion"
    FECHA_INICIAL_TEMPORADA = "fechaInicialTemporada"
    FECHA_FINAL_TEMPORADA = "fechaFinalTemporada"
    COMPOSICION = "codigoAlternoComposicion"
    NOMBRE_COMPOSICION = "nombreComposicion"
    ALTO_PRODUCTO = "altoProducto"
    ANCHO_PRODUCTO = "anchoProducto"
    PROFUNDIDAD_PRODUCTO = "profundidadProducto"
    PESO_BRUTO_PRODUCTO = "pesoBrutoProducto"
    PESO_NETO_PRODUCTO = "pesoNetoProducto"
    POSICION_ARANCELARIA = "codigoAlternoPosicionArancelaria"
    OBSERVACIONES_POSICION_ARANCELARIA= "observacionesPosicionArancelaria"
    DESCRIPCION_DEVOLUCION_ENTREGA_PRODUCTO = "devolucionEntregaProductoDescripcion"
    DESCRIPCION_CUIDADO_PRODUCTO = "cuidadoProductoDescripcion"
    DESCRIPCION_ONLINE_PRODUCTO = "descripcionOnlineProductoDescripcion"
    DESCRIPCION_FIGURA_PRODUCTO = "fitProductoDescripcion"
    ESTRATEGIA_USA = "ESTRATEGIAusa"
    SECCION_USA = "seccionusa"
    EVENTO_USA = "eventousa"
    CLIENTE_OBJECTIVO_USA = "clienteobjetivousa"
    NOMBRE_COLOR_USA = "nombre1Colorusa"
    NOMBRE_COLOR_2_USA = "nombre2colorusa"
    CATEGORIA_USA = "codigoAlterno1Categoriausa"
    DESCRIPCION_CATEGORIA_USA = "DescAlterno1Categoriausa"
    CATEGORIA_USA_2 = "codigoAlterno2Categoriausa"
    DESCRIPCION_CATEGORIA_USA_2 = "DescAlterno2Categoriausa"
    CATEGORIA_USA_3 = "codigoAlterno3Categoriausa"
    DESCRIPCION_CATEGORIA_USA_3 = "DescAlterno3Categoriausa"
    CATEGORIA_USA_4 = "codigoAlterno4Categoriausa"
    DESCRIPCION_CATEGORIA_USA_4 = "DescAlterno4Categoriausa"
    NOMBRE_TEMPORADA_USA = "nombreTemporadausa"
    NOMBRE_COMPOSICION_USA = "nombreComposicionusa"
    DESCRIPCION_DEVOLUCION_ENTREGA_PRODUCTO_USA = "devolucionEntregaProductoDescripcionusa"
    DESCRIPCION_CUIDADO_PRODUCTO_USA = "cuidadoProductoDescripcionusa"
    DESCRIPCION_ONLINE_PRODUCTO_USA = "descripcionOnlineProductoDescripcionusa"
    DESCRIPCION_FIGURA_PRODUCTO_USA = "fitProductoDescripcionusa"
    IMAGEN_PRODUCTO_FUSION = "imagenproductofusion1"
    IVA = "iva"
    FECHA_CREACION = "fechaCreacion"
    IMAGEN = "imagen"
    IMAGEN_2 = "imagen2"
    IMAGEN_3 = "imagen3"
    IMAGEN_4 = "imagen4"

class ProductLine(TypedDict):
    """Estructura de una linea de los productos"""
    CodigCegidArticulos: str
    referenciaProducto: str
    codigoAlternoProducto: str
    nombreLargoProducto: str
    nombreCortoProducto: str
    codigoBarrasProducto: str
    proveedorPrincipal: str
    mascaraDimension: str
    dimension: str
    codigoAlternoTalla: str
    nombre1Talla: str
    dimension2: str
    codigoAlternoColor: str
    nombre1Color: str
    codigoAlternoTemporada: str
    nombreTemporada: str
    cod_grupo: str
    grupo: str
    lineaseccion_COD: str
    lineaseccion_NOMBRE: str
    codigoAlterno1Categoria: str
    DescAlterno1Categoria: str
    codigoAlterno2Categoria: str
    DescAlterno2Categoria: str
    codigoAlterno3Categoria: str
    DescAlterno3Categoria: str
    codigoAlterno4Categoria: str
    DescAlterno4Categoria: str
    codClienteObjetivo: str
    desClienteObjetivo: str
    codigoAlternoTipoNegocio: str
    nombreTipoNegocio: str
    codigoAlternoMarca: str
    nombreMarca: str
    codEvento: str
    desEvento: str
    codigoAlternoPais: str
    nombrePais: str
    codigoAlternoTipoProducto: str
    nombreTipoProducto: str
    familiaTasa1Articulo: str
    precioDetalleImpuestoIncl: str
    estadoProducto: str
    estadoConservacion: str
    fechaCreacionProducto: str
    conceptoProducto: str
    codDIFUSION: str
    DescDIFUSION: str
    codESTRATEGIA: str
    descESTRATEGIA: str
    fechaInicioEvento: str
    fechaFinEvento: str
    nombre2Talla: str
    nombre3Talla: str
    codigoAlternoTallaComplemento: str
    nombre1TallaComplemento: str
    nombre2TallaComplemento: str
    nombre3TallaComplemento: str
    nombre2Color: str
    calificacionEstadoConservacion: str
    fechaInicialTemporada: str
    fechaFinalTemporada: str
    codigoAlternoComposicion: str
    nombreComposicion: str
    altoProducto: str
    anchoProducto: str
    profundidadProducto: str
    pesoBrutoProducto: str
    pesoNetoProducto: str
    codigoAlternoPosicionArancelaria: str
    observacionesPosicionArancelaria: str
    devolucionEntregaProductoDescripcion: str
    cuidadoProductoDescripcion: str
    descripcionOnlineProductoDescripcion: str
    fitProductoDescripcion: str
    ESTRATEGIAusa: str
    seccionusa: str
    eventousa: str
    clienteobjetivousa: str
    nombre1Colorusa: str
    nombre2colorusa: str
    codigoAlterno1Categoriausa: str
    DescAlterno1Categoriausa: str
    codigoAlterno2Categoriausa: str
    DescAlterno2Categoriausa: str
    codigoAlterno3Categoriausa: str
    DescAlterno3Categoriausa: str
    codigoAlterno4Categoriausa: str
    DescAlterno4Categoriausa: str
    nombreTemporadausa: str
    nombreComposicionusa: str
    devolucionEntregaProductoDescripcionusa: str
    cuidadoProductoDescripcionusa: str
    descripcionOnlineProductoDescripcionusa: str
    fitProductoDescripcionusa: str
    imagenproductofusion1: str
    iva: str
    fechaCreacion: str
    imagen: str
    imagen2: str
    imagen3: str
    imagen4: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["ProductLine"]:
        """Comprueba de que el objecto sea tipo `ProductLine`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("id_integracion"), str),
            isinstance(obj.get("CodigCegidArticulos"), str),
            isinstance(obj.get("referenciaProducto"), str),
            isinstance(obj.get("codigoAlternoProducto"), str),
            isinstance(obj.get("nombreLargoProducto"), str),
            isinstance(obj.get("nombreCortoProducto"), str),
            isinstance(obj.get("codigoBarrasProducto"), str),
            isinstance(obj.get("proveedorPrincipal"), str),
            isinstance(obj.get("mascaraDimension"), str),
            isinstance(obj.get("dimension"), str),
            isinstance(obj.get("codigoAlternoTalla"), str),
            isinstance(obj.get("nombre1Talla"), str),
            isinstance(obj.get("dimension2"), str),
            isinstance(obj.get("codigoAlternoColor"), str),
            isinstance(obj.get("nombre1Color"), str),
            isinstance(obj.get("codigoAlternoTemporada"), str),
            isinstance(obj.get("nombreTemporada"), str),
            isinstance(obj.get("cod_grupo"), str),
            isinstance(obj.get("grupo"), str),
            isinstance(obj.get("lineaseccion_COD"), str),
            isinstance(obj.get("lineaseccion_NOMBRE"), str),
            isinstance(obj.get("codigoAlterno1Categoria"), str),
            isinstance(obj.get("DescAlterno1Categoria"), str),
            isinstance(obj.get("codigoAlterno2Categoria"), str),
            isinstance(obj.get("DescAlterno2Categoria"), str),
            isinstance(obj.get("codigoAlterno3Categoria"), str),
            isinstance(obj.get("DescAlterno3Categoria"), str),
            isinstance(obj.get("codigoAlterno4Categoria"), str),
            isinstance(obj.get("DescAlterno4Categoria"), str),
            isinstance(obj.get("codClienteObjetivo"), str),
            isinstance(obj.get("desClienteObjetivo"), str),
            isinstance(obj.get("codigoAlternoTipoNegocio"), str),
            isinstance(obj.get("nombreTipoNegocio"), str),
            isinstance(obj.get("codigoAlternoMarca"), str),
            isinstance(obj.get("nombreMarca"), str),
            isinstance(obj.get("codEvento"), str),
            isinstance(obj.get("desEvento"), str),
            isinstance(obj.get("codigoAlternoPais"), str),
            isinstance(obj.get("nombrePais"), str),
            isinstance(obj.get("codigoAlternoTipoProducto"), str),
            isinstance(obj.get("nombreTipoProducto"), str),
            isinstance(obj.get("familiaTasa1Articulo"), str),
            isinstance(obj.get("precioDetalleImpuestoIncl"), str),
            isinstance(obj.get("estadoProducto"), str),
            isinstance(obj.get("estadoConservacion"), str),
            isinstance(obj.get("fechaCreacionProducto"), str),
            isinstance(obj.get("conceptoProducto"), str),
            isinstance(obj.get("codDIFUSION"), str),
            isinstance(obj.get("DescDIFUSION"), str),
            isinstance(obj.get("codESTRATEGIA"), str),
            isinstance(obj.get("descESTRATEGIA"), str),
            isinstance(obj.get("fechaInicioEvento"), str),
            isinstance(obj.get("fechaFinEvento"), str),
            isinstance(obj.get("nombre2Talla"), str),
            isinstance(obj.get("nombre3Talla"), str),
            isinstance(obj.get("codigoAlternoTallaComplemento"), str),
            isinstance(obj.get("nombre1TallaComplemento"), str),
            isinstance(obj.get("nombre2TallaComplemento"), str),
            isinstance(obj.get("nombre3TallaComplemento"), str),
            isinstance(obj.get("nombre2Color"), str),
            isinstance(obj.get("calificacionEstadoConservacion"), str),
            isinstance(obj.get("fechaInicialTemporada"), str),
            isinstance(obj.get("fechaFinalTemporada"), str),
            isinstance(obj.get("codigoAlternoComposicion"), str),
            isinstance(obj.get("nombreComposicion"), str),
            isinstance(obj.get("altoProducto"), str),
            isinstance(obj.get("anchoProducto"), str),
            isinstance(obj.get("profundidadProducto"), str),
            isinstance(obj.get("pesoBrutoProducto"), str),
            isinstance(obj.get("pesoNetoProducto"), str),
            isinstance(obj.get("codigoAlternoPosicionArancelaria"), str),
            isinstance(obj.get("observacionesPosicionArancelaria"), str),
            isinstance(obj.get("devolucionEntregaProductoDescripcion"), str),
            isinstance(obj.get("cuidadoProductoDescripcion"), str),
            isinstance(obj.get("descripcionOnlineProductoDescripcion"), str),
            isinstance(obj.get("fitProductoDescripcion"), str),
            isinstance(obj.get("ESTRATEGIAusa"), str),
            isinstance(obj.get("seccionusa"), str),
            isinstance(obj.get("eventousa"), str),
            isinstance(obj.get("clienteobjetivousa"), str),
            isinstance(obj.get("nombre1Colorusa"), str),
            isinstance(obj.get("nombre2colorusa"), str),
            isinstance(obj.get("codigoAlterno1Categoriausa"), str),
            isinstance(obj.get("DescAlterno1Categoriausa"), str),
            isinstance(obj.get("codigoAlterno2Categoriausa"), str),
            isinstance(obj.get("DescAlterno2Categoriausa"), str),
            isinstance(obj.get("codigoAlterno3Categoriausa"), str),
            isinstance(obj.get("DescAlterno3Categoriausa"), str),
            isinstance(obj.get("codigoAlterno4Categoriausa"), str),
            isinstance(obj.get("DescAlterno4Categoriausa"), str),
            isinstance(obj.get("nombreTemporadausa"), str),
            isinstance(obj.get("nombreComposicionusa"), str),
            isinstance(obj.get("devolucionEntregaProductoDescripcionusa"), str),
            isinstance(obj.get("cuidadoProductoDescripcionusa"), str),
            isinstance(obj.get("descripcionOnlineProductoDescripcionusa"), str),
            isinstance(obj.get("fitProductoDescripcionusa"), str),
            isinstance(obj.get("imagenproductofusion1"), str),
            isinstance(obj.get("iva"), str),
            isinstance(obj.get("fechaCreacion"), str),
            isinstance(obj.get("imagen"), str),
            isinstance(obj.get("imagen2"), str),
            isinstance(obj.get("imagen3"), str),
            isinstance(obj.get("imagen4"), str)
        ))
