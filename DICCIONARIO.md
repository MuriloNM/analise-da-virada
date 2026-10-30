# Diccionario de datos

Português: [DICIONARIO.md](DICIONARIO.md) · English: [DATA-DICTIONARY.md](DATA-DICTIONARY.md) · 简体中文: [SHUJU-ZIDIAN.md](SHUJU-ZIDIAN.md)

Los archivos de `planilha/`, columna por columna. Los de `planilha/pt-BR/`, `planilha/en/`, `planilha/es/` y `planilha/zh-Hans/` tienen los mismos números; cambian la lengua de los encabezados, el separador y el signo decimal. La unidad y la fórmula de cada columna están en la descripción. Este archivo se genera de `planilha/es/dicionario.csv`.

## municipios.csv

Las dos vueltas lado a lado en los 5757 municipios (5571 de Brasil y 186 del exterior), con los indicadores del estudio.

- **Fuente:** TSE, resultados oficiales (resultados.tse.jus.br, elecciones 6257 y 6258)
- **Hecho por:** `scripts/base1t.py`, `scripts/base2t.py`, `scripts/analise_base.py` → `dados/analise_municipios.csv`
- **Filas:** 5.757

| columna | descripción |
|---|---|
| `cod_tse` | código del municipio en el TSE, 5 dígitos |
| `cod_ibge` | código del municipio en el IBGE, 7 dígitos; vacío en el exterior |
| `estado, municipio` | sigla del estado (ZZ en el exterior) y nombre del municipio |
| `region` | Norte, Nordeste, Centro-Oeste, Sudeste, Sul o Exterior, en portugués (Sul: Sur; nota N08) |
| `capital_interior` | capital, interior o exterior, en portugués (capital del estado, el resto del estado o exterior; nota N08) |
| `tamano, tamano_franja` | franja de tamaño por el electorado de la primera vuelta: código de 1 a 5 (X en el exterior) y nombre, en portugués (nota N08) |
| `electorado_1v, electorado_2v` | electorado habilitado de cada vuelta (nota N05) |
| `votos_emitidos_1v, votos_emitidos_2v` | votos emitidos |
| `abstencion_1v, abstencion_2v` | abstención: electorado − votos emitidos |
| `validos_1v, validos_2v` | votos válidos (en Brasil, excluyen los votos en blanco y los nulos) |
| `blancos_nulos_1v, blancos_nulos_2v` | votos en blanco y nulos: votos emitidos − válidos (en la primera vuelta, juntos: nota N07) |
| `blancos_2v, nulos_2v` | votos en blanco y nulos por separado, solo en la segunda vuelta |
| `lula_1v, flavio_1v, lula_2v, flavio_2v` | votos de cada candidato |
| `otros_1v` | votos de los demás candidatos en la primera vuelta: válidos − Lula − Flávio |
| `parte_lula_1v_pct, parte_lula_2v_pct` | parte de Lula entre los dos, Lula ÷ (Lula + Flávio), en %; vacío si ninguno de los dos tuvo votos (nota N09). La de Flávio es 100 − parte |
| `var_parte_pp` | variación de la parte de Lula, segunda − primera vuelta, en puntos porcentuales |
| `var_lula, var_flavio` | votos ganados por cada uno de la primera a la segunda vuelta |
| `dif_1v, dif_2v, var_dif` | diferencia Lula − Flávio en cada vuelta y su variación |
| `contrib_reversion_pct` | contribución a la reversión: variación de la diferencia de la unidad ÷ la de Brasil, en % |
| `parte_aumento_lula_pct` | parte del aumento: votos ganados por Lula ÷ votos ganados por los dos, en %; vacío cuando los dos juntos no ganaron votos; puede pasar de 100 o quedar por debajo de 0 (nota N09) |
| `var_votos_emitidos` | variación de los votos emitidos, segunda − primera vuelta |
| `var_blancos_nulos` | variación de los votos en blanco y nulos, segunda − primera vuelta |
| `var_electorado` | variación del electorado, segunda − primera vuelta, solo como registro (nota N05) |
| `tasa_abst_1v_pct, tasa_abst_2v_pct` | tasa de abstención: abstención ÷ electorado, en %, cada vuelta con su propio electorado (nota N05) |
| `var_tasa_abst_pp` | variación de la tasa de abstención, en puntos porcentuales |
| `residuo_identidad` | control: (votos ganados por los dos) − (otros de la primera vuelta + variación de los votos emitidos − variación de los votos en blanco y nulos); es cero en todas las filas |

## estados.csv

Las mismas columnas para Brasil, las 5 regiones, el exterior y los 27 estados (el exterior como ZZ).

- **Fuente:** TSE, resultados oficiales (resultados.tse.jus.br, elecciones 6257 y 6258)
- **Hecho por:** `scripts/base1t.py`, `scripts/base2t.py`, `scripts/analise_base.py` → `dados/analise_estados.csv`
- **Filas:** 35

| columna | descripción |
|---|---|
| `nivel` | brasil, regiao o uf, en portugués (Brasil, región o estado) |
| `codigo, nombre` | código (BR, sigla de la región o del estado; ZZ y EX para el exterior) y nombre |
| `region` | región del estado; vacío en Brasil |
| `municipios` | cuántos municipios suma la unidad |
| `electorado_1v, electorado_2v` | electorado habilitado de cada vuelta (nota N05) |
| `votos_emitidos_1v, votos_emitidos_2v` | votos emitidos |
| `abstencion_1v, abstencion_2v` | abstención: electorado − votos emitidos |
| `validos_1v, validos_2v` | votos válidos (en Brasil, excluyen los votos en blanco y los nulos) |
| `blancos_nulos_1v, blancos_nulos_2v` | votos en blanco y nulos: votos emitidos − válidos (en la primera vuelta, juntos: nota N07) |
| `blancos_2v, nulos_2v` | votos en blanco y nulos por separado, solo en la segunda vuelta |
| `lula_1v, flavio_1v, lula_2v, flavio_2v` | votos de cada candidato |
| `otros_1v` | votos de los demás candidatos en la primera vuelta: válidos − Lula − Flávio |
| `parte_lula_1v_pct, parte_lula_2v_pct` | parte de Lula entre los dos, Lula ÷ (Lula + Flávio), en %; vacío si ninguno de los dos tuvo votos (nota N09). La de Flávio es 100 − parte |
| `var_parte_pp` | variación de la parte de Lula, segunda − primera vuelta, en puntos porcentuales |
| `var_lula, var_flavio` | votos ganados por cada uno de la primera a la segunda vuelta |
| `dif_1v, dif_2v, var_dif` | diferencia Lula − Flávio en cada vuelta y su variación |
| `contrib_reversion_pct` | contribución a la reversión: variación de la diferencia de la unidad ÷ la de Brasil, en % |
| `parte_aumento_lula_pct` | parte del aumento: votos ganados por Lula ÷ votos ganados por los dos, en %; vacío cuando los dos juntos no ganaron votos; puede pasar de 100 o quedar por debajo de 0 (nota N09) |
| `var_votos_emitidos` | variación de los votos emitidos, segunda − primera vuelta |
| `var_blancos_nulos` | variación de los votos en blanco y nulos, segunda − primera vuelta |
| `var_electorado` | variación del electorado, segunda − primera vuelta, solo como registro (nota N05) |
| `tasa_abst_1v_pct, tasa_abst_2v_pct` | tasa de abstención: abstención ÷ electorado, en %, cada vuelta con su propio electorado (nota N05) |
| `var_tasa_abst_pp` | variación de la tasa de abstención, en puntos porcentuales |
| `residuo_identidad` | control: (votos ganados por los dos) − (otros de la primera vuelta + variación de los votos emitidos − variación de los votos en blanco y nulos); es cero en todas las filas |

## partidos.csv

Los 30 partidos de 2026, con la posición en la escala de la encuesta a expertos (0 a 10), el bloque de izquierda y las reglas aplicadas.

- **Fuente:** Bolognesi, Ribeiro, Codato e Silva (2025), doi:10.7910/DVN/MFIXKW
- **Hecho por:** `scripts/escala_partidos.py` → `dados/escala_partidos.csv`
- **Filas:** 30

| columna | descripción |
|---|---|
| `numero, sigla, nombre` | número, sigla y nombre del partido en 2026 |
| `federacion_2026` | federación de la que forma parte el partido en 2026, si la hay |
| `posicion` | posición en la escala de la encuesta a expertos, ola de 2022: de 0 (extrema izquierda) a 10 (extrema derecha); vacío en Missão (nota N11) |
| `categoria` | categoría del artículo de origen, en portugués (extrema esquerda, esquerda, centro-esquerda, centro, centro-direita, direita, extrema direita: de extrema izquierda a extrema derecha) |
| `bloque_izquierda` | sí para posición hasta 4,49 (extrema izquierda, izquierda y centroizquierda) |
| `regla, regla_explicada` | regla usada para vincular el partido de 2026 con el de la encuesta (fusiones, cambios de nombre, partidos nuevos: nota N10) |
| `sigla_en_encuesta` | sigla del partido en la base de la encuesta |
| `expertos, desv_estandar` | cuántos expertos dieron calificación y la desviación estándar de las calificaciones (nota N12) |
| `fuente` | la publicación y la base de datos |
| `rob_2018_posicion, rob_2018_bloque_izquierda, rob_2018_regla, rob_2018_explicada` | prueba de robustez con la ola de 2018 de la misma encuesta |
| `rob_zucco_power_2021` | prueba de robustez con la escala de Zucco y Power (encuesta a diputados federales, 2021), de aproximadamente −1 a +1; solo el orden es comparable |

## esquerda_municipios.csv

Voto al bloque de izquierda para diputado y senador en la primera vuelta, por municipio, estado y Brasil (capítulo 5). El del bloque de derecha, del espejo de Flávio, es 100 % menos el de la izquierda y el de los partidos sin posición.

- **Fuente:** TSE, datos abiertos, votacao_partido_munzona_2026.zip; escala en partidos.csv
- **Hecho por:** `scripts/votos_partido_1t.py`, `scripts/escala_partidos.py` → `dados/esquerda_1t_municipios.csv`
- **Filas:** 16.798

| columna | descripción |
|---|---|
| `nivel` | mu (municipio), uf (estado) o br (Brasil) |
| `cod, estado, nombre` | código TSE del municipio (vacío en estado y Brasil), estado y nombre |
| `cargo, cargo_nombre` | 5 senador, 6 deputado federal (diputado federal), 7 deputado estadual (diputado estatal), 8 deputado distrital (diputado distrital) |
| `validos, izq, pct_izq` | votos válidos del cargo, votos de los partidos del bloque de izquierda y su proporción en los válidos, en % |
| `sin_posicion, pct_sin_posicion` | votos del partido sin posición en la escala (Missão) y su proporción en los válidos (nota N11) |
| `escala` | promedio de las posiciones de los partidos, ponderado por los votos, de 0 a 10, solo entre los votos con posición |
| `lula_1v, flavio_1v, parte_lula_1v` | votos para presidente en la primera vuelta y la parte de Lula entre los dos, en % |
| `ventaja` | pct_izq − parte de Lula entre los dos, en puntos porcentuales. La prueba del capítulo 5 usa la proporción sobre los válidos (HIPOTESES.md, P14); esta columna es la de la prueba de robustez |
| `sub_iudice, sub_iudice_izq, pct_izq_con_sj, escala_con_sj, ventaja_con_sj` | la versión con los votos *sub iudice* sumados a los válidos y a sus partidos (nota N02) |
| `rob_2018_pct_izq, rob_2018_sin_posicion, rob_2018_escala, rob_2018_ventaja` | prueba de robustez con la ola de 2018 de la escala |

## votos_partido_1t.csv

Aplanado de `dados/votos_partido_1t.json`, solo en este repositorio: una fila por municipio × cargo × partido con algún voto en la primera vuelta (un partido sin votos en un lugar no tiene fila).

- **Fuente:** TSE, datos abiertos, votacao_partido_munzona_2026.zip
- **Hecho por:** `scripts/votos_partido_1t.py` → `dados/votos_partido_1t.json`
- **Filas:** 318.397

| columna | descripción |
|---|---|
| `estado` | sigla del estado |
| `cod_tse` | código del municipio en el TSE, 5 dígitos (el mismo de municipios.csv) |
| `municipio` | nombre del municipio según la lista del TSE |
| `cargo_codigo, cargo` | cargo en la primera vuelta: 3 gobernador, 5 senador, 6 diputado federal, 7 diputado estatal, 8 diputado distrital (solo en el Distrito Federal, en lugar del estatal) |
| `partido_numero, partido_sigla` | número y sigla del partido |
| `federacion_sigla` | federación de la que forma parte el partido; vacío fuera de una federación |
| `votos_nominales` | votos válidos para candidatos del partido (campo QT_VOTOS_NOMINAIS_VALIDOS del TSE) |
| `votos_partido` | votos válidos solo al número del partido, con los nominales convertidos al partido (QT_TOTAL_VOTOS_LEG_VALIDOS) |
| `votos_validos` | votos válidos del partido: votos_nominales + votos_partido. La suma del cargo en el municipio es igual a los válidos del resultado oficial. Senador: dos bancas en 2026, cada elector votó dos veces, y los válidos superan los votos emitidos |
| `anulados_sub_iudice` | votos anulados sub iudice (nominales + partido), fuera de los válidos como en el resultado oficial; pueden cambiar con una decisión judicial (notas sobre los datos, en Método y fuentes) |
| `anulados` | votos anulados (nominales + partido), fuera de los válidos |

## hipoteses.csv

Las pruebas de las hipótesis de los capítulos 1, 3, 4 y 5: la principal y las de robustez, con intervalo de confianza del 95 %, valor p y clasificación.

- **Fuente:** municipios.csv y esquerda_municipios.csv
- **Hecho por:** `scripts/inferencia.py` → `dados/inferencia.json`
- **Filas:** 59

| columna | descripción |
|---|---|
| `hipotesis, capitulo` | la hipótesis (H1, H3, H4, H5) y el capítulo en que aparece |
| `cargo` | en el capítulo 5, el cargo (deputado federal, deputado estadual o senador: diputado federal, diputado estatal o senador) |
| `version` | la prueba principal o una prueba de robustez |
| `dentro_de_estados` | sí: compara municipios del mismo estado (efecto fijo de estado); no: todos los municipios juntos |
| `peso` | peso de cada municipio en la regresión |
| `variable, controles` | la variable puesta a prueba y los controles |
| `n, grupos` | cuántos municipios y cuántos estados entran |
| `coef, error_estandar` | coeficiente (puntos de variación de la parte de Lula por punto de la variable; en los complementos, sin hipótesis, votos ganados por el candidato en % del electorado de la primera vuelta por punto de la variable) y error estándar agrupado por estado |
| `ic95_inf, ic95_sup` | intervalo de confianza del 95 % del coeficiente por el error agrupado (t con el número de estados menos 1 grados de libertad) |
| `ic95_salvaje_inf, ic95_salvaje_sup` | intervalo del 95 % del bootstrap salvaje, por inversión de la prueba: el que muestran los gráficos (T32) |
| `p_cr1, p_salvaje` | valor p del error agrupado y del bootstrap salvaje por conglomerados (vacío donde no se calculó) |
| `r2, r2_tipo` | R² y de qué tipo (comum o dentro dos estados: común o dentro de los estados) |
| `efecto_intercuartil_pp` | diferencia prevista en la variación de la parte de Lula entre un municipio del cuartil inferior y uno del cuartil superior de la variable, en puntos |
| `previsto, clasificacion, pequena` | signo previsto antes de los cálculos, la clasificación (confirmada, contrária o inconclusiva: respaldada, contradicha o no concluyente) y si la asociación es pequeña (menos de 0,5 puntos) |

## de_onde_vieram.csv

De dónde vinieron los votos ganados por cada uno, en Brasil, por región y por estado, comparando secciones electorales de la misma ciudad, con el intervalo de confianza del 95 % y el criterio de precisión.

- **Fuente:** TSE, datos abiertos y boletines de urna por sección (dados/secoes_presidente.csv.gz)
- **Hecho por:** `scripts/secoes_baixar.py`, `scripts/secoes.py`, `scripts/secoes_inferencia.py`, `scripts/inferencia.py` → `dados/inferencia.json`
- **Filas:** 99

| columna | descripción |
|---|---|
| `nivel, lugar, n` | Brasil, región o estado, y cuántos municipios entran (con todas sus secciones) |
| `fuente` | la fuente de los votos ganados: votos de los demás candidatos de la primera vuelta, variación de los votos emitidos o caída de los votos en blanco y nulos |
| `lula, lula_ic95_inf, lula_ic95_sup` | la parte de la fuente que quedó, en saldo, con Lula (de 0 a 1) y el intervalo de confianza del 95 % por bootstrap (ver la columna intervalo) |
| `flavio, flavio_ic95_inf, flavio_ic95_sup` | lo mismo para Flávio (las dos partes suman 1) |
| `semiamplitud` | mitad del ancho del intervalo de confianza del 95 %, de 0 a 1 |
| `cumple_criterio` | sí cuando cumple el criterio de precisión (al menos 30 municipios, estimación entre 0 y 1 y semiamplitud hasta 0,10; HIPOTESES.md 4.2, con el orden del T32) |
| `mayor_parte, motivo` | con quién quedó la mayor parte, cuando cumple; el motivo, cuando no cumple (nota N16) |
| `intervalo` | qué remuestreó el bootstrap: estados enteros (Brasil y regiones) o municipios enteros, con todas sus secciones (estados) |
| `aviso_modelo` | sí cuando alguna fuente del lugar sale del rango de 0 a 1: el modelo no describe bien el lugar, y todas sus fuentes llevan el aviso (marca † en la página) |

## apuracao_ao_vivo.csv

Las lecturas que grabó la página del escrutinio en vivo de la segunda vuelta: % escrutado, hora, conteo, primera vuelta en las mismas urnas y proyección (capítulo 7 y Escrutinio en vivo).

- **Fuente:** lecturas grabadas de la página del escrutinio en vivo (resultados.tse.jus.br, elección 6258), 25/10/2026
- **Hecho por:** `scripts/collector.py` → `dados/historico_2t.json`
- **Filas:** 115

| columna | descripción |
|---|---|
| `urnas_escrutadas_pct, hora_tse` | % de las urnas escrutadas en la lectura y la hora de la lectura en el TSE |
| `lula_2v_pct` | parte de Lula entre los dos en el conteo de la segunda vuelta hasta esa lectura, en % |
| `lula_1v_mismas_urnas_pct` | parte de Lula en la primera vuelta en las mismas urnas ya escrutadas en la segunda, en % |
| `proyeccion_final_pct` | proyección del resultado final mostrada en vivo, en % (parte de Lula) |
| `lula_1v_por_estado_pct` | parte de Lula en la primera vuelta en las mismas urnas tomadas solo por estado, en % (control de la página en vivo) |

## testes_sociais.csv

Las 35 pruebas de los datos sociales del capítulo 8 (7 características × 5 medidas), dentro de los estados y en Brasil, con intervalo de confianza del 95 %, valor p, valor p corregido por Holm y resultado.

- **Fuente:** municipios.csv y dados_sociais.csv
- **Hecho por:** `scripts/inferencia.py` → `dados/inferencia.json`
- **Filas:** 70

| columna | descripción |
|---|---|
| `variable, resultado` | la característica del municipio y la medida de la elección: ds (variación de la parte de Lula), gL y gF (votos ganados por Lula y por Flávio, en % del electorado de la primera vuelta), cap (parte de Lula en los votos que ganaron los dos) y da (variación de la abstención) |
| `dentro_de_estados` | sí: compara municipios del mismo estado (la versión que decide); no: todos los municipios juntos |
| `n, grupos` | cuántos municipios y cuántos estados entran |
| `coef, error_estandar` | coeficiente (puntos de la medida por 1 punto de la característica; por 1 unidad de logaritmo en el PIB per cápita y en la densidad) y error estándar agrupado por estado |
| `ic95_inf, ic95_sup` | intervalo de confianza del 95 % del coeficiente por el error agrupado |
| `ic95_salvaje_inf, ic95_salvaje_sup` | intervalo del 95 % del bootstrap salvaje, por inversión de la prueba |
| `p_cr1, p_salvaje` | valor p del error agrupado y del bootstrap salvaje |
| `p_holm, p_cr1_holm` | los dos valores p corregidos por el método de Holm en las 35 pruebas de la misma versión |
| `efecto_intercuartil` | diferencia prevista en la medida entre un municipio del cuartil inferior y uno del cuartil superior de la característica, en puntos |
| `asociacion, direccion, pequena` | sí cuando los dos valores p corregidos quedan por debajo de 0,05; la dirección (positiva o negativa) y si es pequeña (menos de 0,5 puntos entre cuartiles) |

## dados_sociais.csv

Las 7 características de cada municipio del capítulo 8 (IBGE, Censo de 2022 y PIB de los Municipios 2023), con las bases de cada una.

- **Fuente:** IBGE: Censo 2022 (SIDRA), PIB dos Municípios 2023, Áreas Territoriais 2022
- **Hecho por:** `scripts/sociais_baixar.py`, `scripts/dados_sociais.py` → `dados/dados_sociais_municipios.json`
- **Filas:** 5.571

| columna | descripción |
|---|---|
| `cod_tse, cod_ibge, estado, municipio` | código del municipio en el TSE (5 dígitos) y en el IBGE (7 dígitos), estado y nombre |
| `pct_60ymas` | % de la población residente de 60 años o más (Censo de 2022) |
| `alfab_15ymas` | tasa de alfabetización de las personas de 15 años o más, en %, como la publica el IBGE (Censo de 2022) |
| `pct_ingreso_hasta_medio_sm` | % de residentes en hogares particulares permanentes con ingreso domiciliario per cápita de hasta medio salario mínimo, incluidos los que no tienen ingresos (Censo de 2022, muestra) |
| `pib_pc, ln_pib_pc` | PIB per cápita de 2023, en reales, como lo publica el IBGE, y su logaritmo natural, que es el que se usa en las pruebas |
| `densidad, ln_densidad` | habitantes por km² (Censo de 2022), como la publica el IBGE, y su logaritmo natural, que se usa en las pruebas |
| `pct_evangelicos` | % de evangélicos entre las personas de 10 años o más (Censo de 2022, muestra; nota N19) |
| `pct_negros_pardos` | % de negros y pardos (categorías del IBGE: pretos y pardos) en la población residente (Censo de 2022) |
| `pob, pob15, pob10, area_km2, pib_mil` | las bases: población residente, de 15 años o más y de 10 años o más, área en km² y PIB de 2023 en miles de reales; todo vacío en Boa Esperança do Norte (MT), nota N20 |
