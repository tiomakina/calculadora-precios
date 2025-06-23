import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Precios - Chile",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f2937;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.success-card {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 1rem 0;
}
.warning-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 1rem 0;
}
.info-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'productos' not in st.session_state:
    st.session_state.productos = []
if 'config' not in st.session_state:
    st.session_state.config = {
        'iva': 19.0,
        'margen_defecto': 30.0,
        'metodo_calculo': 'margen'
    }

# Categorías de costos
CATEGORIAS_COSTOS = {
    'logisticos': {
        'titulo': 'Costos Logísticos',
        'descripcion': 'Transporte, almacenamiento y distribución',
        'campos': [
            ('transporte', 'Transporte', 'Costo de traslado de mercancías'),
            ('almacenamiento', 'Almacenamiento', 'Costo de bodegaje y manejo de inventario'),
            ('combustible', 'Combustible', 'Gastos de combustible para transporte'),
            ('envio', 'Envío', 'Costo de entrega al cliente final')
        ]
    },
    'personal': {
        'titulo': 'Costos de Personal',
        'descripcion': 'Mano de obra y servicios profesionales',
        'campos': [
            ('mano_obra', 'Mano de Obra', 'Costo directo de trabajadores en producción'),
            ('hora_hombre', 'Hora Hombre', 'Servicios profesionales y consultoría')
        ]
    },
    'operativos': {
        'titulo': 'Costos Operativos',
        'descripcion': 'Marketing, seguros y promoción',
        'campos': [
            ('marketing', 'Marketing', 'Gastos en publicidad y promoción'),
            ('publicidad', 'Publicidad Digital', 'Anuncios online y campañas digitales'),
            ('seguros', 'Seguros', 'Pólizas de seguro para productos/servicios')
        ]
    },
    'administrativos': {
        'titulo': 'Costos Administrativos',
        'descripcion': 'Gastos generales de funcionamiento',
        'campos': [
            ('alquiler', 'Alquiler/Instalaciones', 'Arriendo de oficinas o locales'),
            ('servicios_basicos', 'Servicios Básicos', 'Luz, agua, gas'),
            ('internet', 'Internet', 'Conexión a internet y telecomunicaciones'),
            ('telefono', 'Teléfono', 'Servicios telefónicos')
        ]
    },
    'financieros': {
        'titulo': 'Costos Financieros',
        'descripcion': 'Intereses y comisiones bancarias',
        'campos': [
            ('intereses', 'Intereses', 'Intereses por financiamiento'),
            ('comisiones_bancarias', 'Comisiones Bancarias', 'Gastos bancarios y financieros')
        ]
    },
    'otros': {
        'titulo': 'Otros Costos',
        'descripcion': 'Mantenimiento y gastos varios',
        'campos': [
            ('mantenimiento', 'Mantenimiento', 'Reparaciones y mantenimiento de equipos'),
            ('depreciacion', 'Depreciación', 'Depreciación de equipos y maquinaria'),
            ('gastos_generales', 'Gastos Generales', 'Otros gastos no categorizados')
        ]
    }
}

def calcular_precios(costo_base, costos_adicionales, margen, iva, metodo_calculo):
    """Calcula precios usando metodología empresarial correcta"""
    costo_base = float(costo_base) if costo_base else 0
    costos_adicionales = float(costos_adicionales) if costos_adicionales else 0
    margen = float(margen) if margen else 0
    iva = float(iva) if iva else 0
    
    # Costo total = Costo base + Costos adicionales
    costo_total = costo_base + costos_adicionales
    
    if metodo_calculo == 'margen':
        # MÉTODO MARGEN (sobre precio de venta) - Metodología profesional
        # Precio = Costo / (1 - Margen%)
        if margen >= 100:
            margen = 99  # Evitar división por cero
        precio_sin_iva = costo_total / (1 - margen / 100)
        margen_real_sobre_ventas = margen
        markup_real_sobre_costo = ((precio_sin_iva - costo_total) / costo_total) * 100 if costo_total > 0 else 0
    else:
        # MÉTODO MARKUP (sobre costo) - Metodología tradicional
        # Precio = Costo × (1 + Markup%)
        precio_sin_iva = costo_total * (1 + margen / 100)
        markup_real_sobre_costo = margen
        margen_real_sobre_ventas = ((precio_sin_iva - costo_total) / precio_sin_iva) * 100 if precio_sin_iva > 0 else 0
    
    # Precio con IVA
    precio_con_iva = precio_sin_iva * (1 + iva / 100)
    
    # Ganancia bruta
    ganancia = precio_sin_iva - costo_total
    
    # Valor del IVA
    valor_iva = precio_con_iva - precio_sin_iva
    
    # Descuento máximo sin pérdidas
    descuento_maximo = ((precio_con_iva - costo_total) / precio_con_iva) * 100 if precio_con_iva > 0 else 0
    precio_con_descuento_maximo = precio_con_iva * (1 - descuento_maximo / 100)
    
    return {
        'costo_base': costo_base,
        'costos_adicionales': costos_adicionales,
        'costo_total': costo_total,
        'precio_sin_iva': precio_sin_iva,
        'precio_con_iva': precio_con_iva,
        'valor_iva': valor_iva,
        'ganancia': ganancia,
        'margen_porcentaje': margen,
        'margen_real_sobre_ventas': margen_real_sobre_ventas,
        'markup_real_sobre_costo': markup_real_sobre_costo,
        'descuento_maximo': descuento_maximo,
        'precio_con_descuento_maximo': precio_con_descuento_maximo,
        'iva': iva,
        'metodo_calculo': metodo_calculo
    }

def formatear_peso(valor):
    """Formatea valores en pesos chilenos"""
    return f"${valor:,.0f}".replace(",", ".")

def crear_csv_productos(productos):
    """Crea CSV para exportar"""
    if not productos:
        return None
    
    df = pd.DataFrame(productos)
    df.columns = [
        'Nombre', 'Costo Base', 'Costos Adicionales', 'Costo Total',
        'Método Cálculo', 'Margen Real Ventas %', 'Markup Real Costo %',
        'Precio Neto', 'IVA', 'Precio Final', 'Ganancia', 'Descuento Máximo %'
    ]
    return df

# HEADER
st.markdown('<h1 class="main-header">🧮 Calculadora de Precios Avanzada - Chile</h1>', unsafe_allow_html=True)

# SIDEBAR - Configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # IVA
    st.session_state.config['iva'] = st.number_input(
        "IVA (%)",
        min_value=0.0,
        max_value=30.0,
        value=st.session_state.config['iva'],
        step=0.1,
        help="Impuesto al Valor Agregado (19% en Chile)"
    )
    
    # Método de cálculo
    st.session_state.config['metodo_calculo'] = st.selectbox(
        "Metodología de Cálculo",
        ['margen', 'markup'],
        format_func=lambda x: 'Margen (Profesional)' if x == 'margen' else 'Markup (Tradicional)',
        index=0 if st.session_state.config['metodo_calculo'] == 'margen' else 1,
        help="Margen = sobre precio de venta (recomendado). Markup = sobre costo"
    )
    
    # Margen por defecto
    label_margen = "Margen por defecto (%)" if st.session_state.config['metodo_calculo'] == 'margen' else "Markup por defecto (%)"
    st.session_state.config['margen_defecto'] = st.number_input(
        label_margen,
        min_value=0.0,
        max_value=200.0,
        value=st.session_state.config['margen_defecto'],
        step=1.0
    )
    
    st.markdown("---")
    
    # Mostrar explicación
    if st.checkbox("📖 Ver Explicación"):
        st.markdown("""
        ### 📊 Metodologías Empresariales:
        
        **🟢 MARGEN (Recomendado):**
        - Precio = Costo / (1 - Margen%)
        - Más preciso, usado por empresas profesionales
        
        **🟡 MARKUP (Tradicional):**
        - Precio = Costo × (1 + Markup%)
        - Más simple pero menos preciso
        
        **⚠️ Importante:** Un Markup 50% = solo 33% de margen real sobre ventas
        """)

# FORMULARIO PRINCIPAL
st.header("➕ Agregar Producto/Servicio")

with st.form("producto_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nombre = st.text_input("Nombre del producto/servicio", placeholder="Ej: Laptop HP / Consultoría SEO")
    
    with col2:
        costo_base = st.number_input("Costo base ($)", min_value=0.0, step=1000.0, format="%.0f")
    
    with col3:
        margen_label = "Margen sobre ventas (%)" if st.session_state.config['metodo_calculo'] == 'margen' else "Markup sobre costo (%)"
        margen_producto = st.number_input(
            margen_label, 
            min_value=0.0, 
            max_value=200.0, 
            value=st.session_state.config['margen_defecto'], 
            step=1.0
        )
    
    # Costos avanzados
    mostrar_costos_avanzados = st.checkbox("🔧 Mostrar Costos Avanzados")
    
    costos_adicionales = {}
    if mostrar_costos_avanzados:
        st.markdown("### 💼 Costos Adicionales")
        
        for categoria_key, categoria in CATEGORIAS_COSTOS.items():
            with st.expander(f"{categoria['titulo']} - {categoria['descripcion']}"):
                cols = st.columns(2)
                for i, (campo_key, campo_label, campo_desc) in enumerate(categoria['campos']):
                    col_idx = i % 2
                    with cols[col_idx]:
                        costos_adicionales[campo_key] = st.number_input(
                            f"{campo_label} ($)",
                            min_value=0.0,
                            step=100.0,
                            format="%.0f",
                            help=campo_desc,
                            key=f"costo_{campo_key}"
                        )
    
    agregar_producto = st.form_submit_button("✅ Agregar Producto", use_container_width=True)

# Procesar formulario
if agregar_producto:
    if nombre and costo_base > 0:
        # Calcular costos adicionales totales
        total_costos_adicionales = sum(costos_adicionales.values())
        
        # Calcular precios
        resultado = calcular_precios(
            costo_base, 
            total_costos_adicionales, 
            margen_producto, 
            st.session_state.config['iva'],
            st.session_state.config['metodo_calculo']
        )
        
        # Agregar producto a la lista
        producto = {
            'nombre': nombre,
            'costo_base': resultado['costo_base'],
            'costos_adicionales': resultado['costos_adicionales'],
            'costo_total': resultado['costo_total'],
            'metodo_calculo': resultado['metodo_calculo'],
            'margen_real_sobre_ventas': resultado['margen_real_sobre_ventas'],
            'markup_real_sobre_costo': resultado['markup_real_sobre_costo'],
            'precio_sin_iva': resultado['precio_sin_iva'],
            'valor_iva': resultado['valor_iva'],
            'precio_con_iva': resultado['precio_con_iva'],
            'ganancia': resultado['ganancia'],
            'descuento_maximo': resultado['descuento_maximo']
        }
        
        st.session_state.productos.append(producto)
        st.success(f"✅ {nombre} agregado correctamente!")
        st.rerun()
    else:
        st.error("❌ Por favor ingresa nombre y costo base")

# VISTA PREVIA DEL CÁLCULO
if nombre and costo_base > 0:
    st.markdown("### 👁️ Vista Previa del Cálculo")
    
    total_costos_adicionales = sum(costos_adicionales.values()) if costos_adicionales else 0
    preview = calcular_precios(
        costo_base, 
        total_costos_adicionales, 
        margen_producto, 
        st.session_state.config['iva'],
        st.session_state.config['metodo_calculo']
    )
    
    # Métricas principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Costo Base", formatear_peso(preview['costo_base']))
    with col2:
        st.metric("Costos Adicionales", formatear_peso(preview['costos_adicionales']))
    with col3:
        st.metric("Costo Total", formatear_peso(preview['costo_total']))
    with col4:
        st.metric("Precio Neto", formatear_peso(preview['precio_sin_iva']))
    with col5:
        st.metric("IVA", formatear_peso(preview['valor_iva']))
    with col6:
        st.metric("Precio Final", formatear_peso(preview['precio_con_iva']))
    
    # Información adicional
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ganancia", formatear_peso(preview['ganancia']))
    with col2:
        st.metric("Margen Real s/Ventas", f"{preview['margen_real_sobre_ventas']:.1f}%")
    with col3:
        st.metric("Markup Real s/Costo", f"{preview['markup_real_sobre_costo']:.1f}%")
    with col4:
        st.metric("Descuento Máximo", f"{preview['descuento_maximo']:.1f}%")
    
    # Alerta de descuento máximo
    st.markdown(f"""
    <div class="warning-card">
        <strong>💡 Descuento máximo sin pérdidas:</strong> {preview['descuento_maximo']:.1f}%<br>
        <strong>Precio mínimo:</strong> {formatear_peso(preview['costo_total'])} (punto de equilibrio)
    </div>
    """, unsafe_allow_html=True)
    
    # Alerta si hay diferencia entre Markup y Margen
    if (st.session_state.config['metodo_calculo'] == 'markup' and 
        abs(preview['markup_real_sobre_costo'] - preview['margen_real_sobre_ventas']) > 0.1):
        st.markdown(f"""
        <div class="info-card">
            ⚠️ <strong>Nota:</strong> Tu Markup de {preview['markup_real_sobre_costo']:.1f}% equivale a solo {preview['margen_real_sobre_ventas']:.1f}% de margen real sobre ventas.
        </div>
        """, unsafe_allow_html=True)

# IMPORTAR/EXPORTAR
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Importar CSV")
    uploaded_file = st.file_uploader("Seleccionar archivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Procesar cada fila
            productos_importados = 0
            for _, row in df.iterrows():
                if 'nombre' in df.columns and 'costo_base' in df.columns:
                    nombre_imp = row.get('nombre', '')
                    costo_base_imp = row.get('costo_base', 0)
                    margen_imp = row.get('margen', st.session_state.config['margen_defecto'])
                    
                    if nombre_imp and costo_base_imp > 0:
                        # Calcular costos adicionales de las columnas del CSV
                        costos_add_imp = 0
                        for categoria in CATEGORIAS_COSTOS.values():
                            for campo_key, _, _ in categoria['campos']:
                                costos_add_imp += row.get(campo_key, 0)
                        
                        resultado_imp = calcular_precios(
                            costo_base_imp, 
                            costos_add_imp, 
                            margen_imp, 
                            st.session_state.config['iva'],
                            st.session_state.config['metodo_calculo']
                        )
                        
                        producto_imp = {
                            'nombre': nombre_imp,
                            'costo_base': resultado_imp['costo_base'],
                            'costos_adicionales': resultado_imp['costos_adicionales'],
                            'costo_total': resultado_imp['costo_total'],
                            'metodo_calculo': resultado_imp['metodo_calculo'],
                            'margen_real_sobre_ventas': resultado_imp['margen_real_sobre_ventas'],
                            'markup_real_sobre_costo': resultado_imp['markup_real_sobre_costo'],
                            'precio_sin_iva': resultado_imp['precio_sin_iva'],
                            'valor_iva': resultado_imp['valor_iva'],
                            'precio_con_iva': resultado_imp['precio_con_iva'],
                            'ganancia': resultado_imp['ganancia'],
                            'descuento_maximo': resultado_imp['descuento_maximo']
                        }
                        
                        st.session_state.productos.append(producto_imp)
                        productos_importados += 1
            
            if productos_importados > 0:
                st.success(f"✅ {productos_importados} productos importados correctamente!")
                st.rerun()
            else:
                st.error("❌ No se pudieron importar productos. Verifica el formato del CSV.")
                
        except Exception as e:
            st.error(f"❌ Error al importar CSV: {str(e)}")

with col2:
    st.subheader("📥 Exportar CSV")
    
    if st.session_state.productos:
        df_productos = crear_csv_productos(st.session_state.productos)
        csv = df_productos.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name=f"precios_calculados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.info(f"📊 {len(st.session_state.productos)} productos listos para exportar")
    else:
        st.info("📝 Agrega productos para poder exportar")

# Formato CSV
st.markdown("""
**Formato CSV básico:** `nombre,costo_base,margen_opcional`  
**Ejemplo:** `"Consultoría Web",500000,40`  
El CSV exportado incluye: costos, precios, márgenes y **descuentos máximos**
""")

# TABLA DE PRODUCTOS
if st.session_state.productos:
    st.markdown("---")
    st.header(f"📊 Productos/Servicios Calculados ({len(st.session_state.productos)})")
    
    # Crear DataFrame para mostrar
    df_display = pd.DataFrame(st.session_state.productos)
    
    # Formatear columnas monetarias
    columnas_dinero = ['costo_base', 'costos_adicionales', 'costo_total', 'precio_sin_iva', 'valor_iva', 'precio_con_iva', 'ganancia']
    for col in columnas_dinero:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: formatear_peso(x))
    
    # Formatear columnas de porcentaje
    columnas_porcentaje = ['margen_real_sobre_ventas', 'markup_real_sobre_costo', 'descuento_maximo']
    for col in columnas_porcentaje:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}%")
    
    # Renombrar columnas para mejor visualización
    df_display.columns = [
        'Producto/Servicio', 'Costo Base', 'Costos Adic.', 'Costo Total',
        'Método', 'Margen Real', 'Markup Real', 'Precio Neto', 'IVA',
        'Precio Final', 'Ganancia', 'Desc. Máximo'
    ]
    
    # Mostrar tabla
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Botón para limpiar productos
    if st.button("🗑️ Limpiar todos los productos", type="secondary"):
        st.session_state.productos = []
        st.success("✅ Productos eliminados")
        st.rerun()
    
    # RESUMEN EJECUTIVO
    st.markdown("### 📈 Resumen Ejecutivo")
    
    # Calcular totales
    total_costo_base = sum(p['costo_base'] for p in st.session_state.productos)
    total_costos_adicionales = sum(p['costos_adicionales'] for p in st.session_state.productos)
    total_inversion = sum(p['costo_total'] for p in st.session_state.productos)
    total_neto = sum(p['precio_sin_iva'] for p in st.session_state.productos)
    total_iva = sum(p['valor_iva'] for p in st.session_state.productos)
    total_final = sum(p['precio_con_iva'] for p in st.session_state.productos)
    total_ganancia = sum(p['ganancia'] for p in st.session_state.productos)
    
    # Métricas del resumen
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Costo Base", formatear_peso(total_costo_base))
    with col2:
        st.metric("Total Costos Adic.", formatear_peso(total_costos_adicionales))
    with col3:
        st.metric("Total Inversión", formatear_peso(total_inversion))
    with col4:
        st.metric("Total Neto", formatear_peso(total_neto))
    with col5:
        st.metric("Total IVA", formatear_peso(total_iva))
    with col6:
        st.metric("Total Final", formatear_peso(total_final))
    
    # Métricas de rentabilidad
    col1, col2, col3 = st.columns(3)
    
    margen_promedio = np.mean([p['margen_real_sobre_ventas'] for p in st.session_state.productos])
    roi = ((total_final / total_inversion) - 1) * 100 if total_inversion > 0 else 0
    descuento_promedio = np.mean([p['descuento_maximo'] for p in st.session_state.productos])
    
    with col1:
        st.markdown(f"""
        <div class="success-card">
            <strong>💰 Ganancia Total:</strong> {formatear_peso(total_ganancia)}<br>
            <strong>📊 Margen Promedio:</strong> {margen_promedio:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <strong>📈 ROI:</strong> {roi:.1f}%<br>
            <strong>🔧 Metodología:</strong> {st.session_state.config['metodo_calculo'].title()}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="warning-card">
            <strong>🎯 Descuento Máx. Promedio:</strong> {descuento_promedio:.1f}%<br>
            <strong>💸 Precio Mín. Promedio:</strong> {formatear_peso(total_inversion / len(st.session_state.productos) if st.session_state.productos else 0)}
        </div>
        """, unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🧮 <strong>Calculadora de Precios Avanzada - Chile</strong></p>
    <p>✅ Costos avanzados | ✅ Metodologías empresariales | ✅ Descuentos máximos | ✅ Análisis completo</p>
    <p><em>Creado con Python + Streamlit</em></p>
</div>
""", unsafe_allow_html=True)
