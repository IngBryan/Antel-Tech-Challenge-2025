from enum import Enum
from typing import List, Optional, Union, Set
from pydantic import BaseModel, Field, ConfigDict
import json


class Incidencia(BaseModel):
    fecha: str = Field(description="Fecha de incidencia en formato XX-XX-XX.")
    motivo: str = Field(description="Resumen del motivo de la incidencia.")


class Reclamos(BaseModel):
    # campania: str = Field(description="Por ejemplo Reclamos_611")
    total_llamadas: int = Field(
        title="",
        description="Total cantidad de llamadas al Sistema de Reclamos de ANTEL. Se obtiene ",
    )
    tiempo_total: str = Field(
        title="", description="Tiempo total de reclamos en formato hh:mm:ss"
    )


class MotivosIZI611(BaseModel):
    nombre_de_codigo_de_conclusion: str = Field(
        title="Nombre de código de conclusión",
        description='Se obtiene del archivo en la columna "Nombre de código de conclusión", por ejemplo "Información General - 611", "Cliente no responde - 611", "Facturacion - 611"',
    )
    manejo: int = Field(
        title="Manejo",
        description='Se obtiene del archivo en partir de la columna "Manejo". Cuidado, no te confundas con otras columnas de nombre similar!.',
    )


class AntelMovil611(BaseModel):
    llamadas_al_servicio: int = Field(
        description="Se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Ofrecidas”. Observar que este valor debe coincidir con el que se encuentra en la columna “Ofrecidas” a partir de “Habilidad” en la fila “ANTEL MOVIL”"
    )
    llamadas_atendidas_totales: int = Field(
        description="se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Atendidas”.  Observar que este valor debe coincidir con el que se encuentra en la columna “Contestadas” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    llamadas_abandonadas: int = Field(
        description="se calcula a partir de “Listado de llamadas Atendidas y Abandonadas - Habilidad/Fecha” como la suma total de los valores de la columna “Abandonada”. Observar que este valor debe coincidir con el que se encuentra en la columna “Abandonadas” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    porcentaje_llamadas_no_atendidas: float = Field(
        "se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Indice de Abandono %”"
    )
    cumplimiento_servicio: float = Field(
        description="Porcentaje de cumplimiento del nivel de servicio acordado, donde 80% de nivel de servicio equivale al 100% de cumplimiento. Operación: Nivel de servicio / 80%."
    )
    indice_respuesta: float = Field(
        description="(Llamadas atendidas totales / Llamadas al servicio) %.  Observar que este valor debe coincidir con el que se encuentra en la columna “Indice de respuesta %” a partir de “Habilidad” en la fila “ANTEL MOVIL”."
    )
    trsac: int = Field(
        description="Demora de atención. La cantidad de segundos que un cliente espera en promedio en ser atendido. Operación: Total de demora en atender(segundos) / Total de llamadas atendidas."
    )
    promedio_operacion: float = Field(
        title="Promedio Operación",
        description="Se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Tiempo Operación”",
    )
    atencion: float = Field(
        title="Tiempo de Atención",
        description="se obtiene a partir de “Habilidad” en la fila “ANTEL MOVIL” columna “Horas Operación”",
    )
    congestion: int = Field(
        description="Cantidad de llamadas que la central devolvió tono ocupado. Operación: Llamadas_con_tono_ocupado / Cantidad_de_intento. Se puede obtener a partir de “Reporte de Calificaciones” en la columna “611(%)” sumando la congestión de cada día, dividiéndola por la cantidad de días."
    )


class Whatsapp(BaseModel):
    entrantes: int = Field(
        title="Cantidad de mensajes entrantes",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Cantidad de mensajes entrantes”",
    )
    salientes: int = Field(
        title="Cantidad de mensajes salientes",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Cantidad de mensajes salientes”",
    )
    total: int = Field(
        title="Total de mensajes",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Total de mensajes”",
    )
    promedio: float = Field(
        title="Promedio de mensajes por interacción",
        description="se obtiene a partir de “Resumen de Campanas Heynow” en la fila “Roaming” columna “Promedio de mensajes por interacción”",
    )


class Salientes(BaseModel):
    movil_contratos: int = Field(
        description="Total de llamadas salientes respecto a MOVIL_Contratos. Se obtiene de la columna “Saliente”."
    )
    movil_prepagos: int = Field(
        description="Total de llamadas salientes respecto a MOVIL_Prepagos. Se obtiene de la columna “Saliente”"
    )
    movil_prioritarios: int = Field(
        description="Total de llamadas salientes respecto a MOVIL_Prioritarios. Se obtiene de la columna “Saliente”"
    )
    salientes_movil: int = Field(
        description="Total de llamadas salientes respecto a Salientes_movil. Se obtiene de la columna “Saliente”"
    )


class Reporte(BaseModel):
    antel_movil: AntelMovil611
    incidencias: list[Incidencia] = Field(description="Incidencias relevantes.")
    reclamos: Reclamos
    motivosIzi611: list[MotivosIZI611] = Field(
        description='Lista no vacia!. Lista de valores de la columna "Manejo" para cada \'Nombre de código de conclusión\'. Esta lista se obtiene a partir del archivo "2025-05-19 Rendimiento de conclusión - tipif. Reclamos"'
    )
    whatsapp: Whatsapp
    salientes: Salientes


print(Reporte.model_json_schema())
