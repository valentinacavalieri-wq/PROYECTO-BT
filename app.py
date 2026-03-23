import streamlit as st
import pandas as pd
import base64
import re
import io

def estandarizar_ciudad(ciudad):
    if pd.isna(ciudad): return ""
    c = str(ciudad).strip().upper()
    # Remover acentos básicos
    c = c.replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U')
    
    mapa_ciudades = {
        "ANACO": "ANA", "ANA": "ANA", "ARAURE": "ARA", "ARA": "ARA",
        "BARINAS": "BAR", "BAR": "BAR", "BARQUISIMETO": "BQTO", "BQTO": "BQTO",
        "BARCELONA": "BRC", "BRC": "BRC", "CARORA": "CAR", "CAR": "CAR",
        "CALABOZO": "CAL", "CAL": "CAL", "CABUDARE": "CABU", "CABU": "CABU",
        "CABIMAS": "CBMA", "CBMA": "CBMA", "CIUDAD BOLIVAR": "CBOL", "CBOL": "CBOL",
        "CARACAS": "CCS", "CCS": "CCS", "CIUDAD OJEDA": "CDOJ", "CDOJ": "CDOJ",
        "CHARALLAVE": "CHAR", "CHAR": "CHAR", "CATIA LA MAR": "CMAR", "CMAR": "CMAR",
        "CUMANA": "CMNA", "CMNA": "CMNA", "CORO": "COR", "COR": "COR",
        "CUA": "CUA", "CARUPANO": "CRNO", "CRNO": "CRNO", "GUANARE": "GNRE", "GNRE": "GNRE",
        "GUARENAS": "GRNA", "GRNA": "GRNA", "GUACARA": "GUAC", "GUAC": "GUAC",
        "GUATIRE": "GUAT", "GUAT": "GUAT", "HIGUEROTE": "HIG", "HIG": "HIG",
        "LECHERIA": "LEC", "LEC": "LEC", "LOS TEQUES": "LTQU", "LTQU": "LTQU",
        "LA VICTORIA": "LVIC", "LVIC": "LVIC", "MATURIN": "MAT", "MAT": "MAT",
        "MARACAIBO": "MCBO", "MCBO": "MCBO", "MERIDA": "MER", "MER": "MER",
        "MARACAY": "MRCY", "MRCY": "MRCY", "PAMPATAR": "PAM", "PAM": "PAM",
        "PORLAMAR": "POR", "POR": "POR", "PUNTA DE MATA": "PDM", "PDM": "PDM",
        "PUNTO FIJO": "PTJO", "PTJO": "PTJO", "PUERTO LA CRUZ": "PTLC", "PTLC": "PTLC",
        "PUERTO CABELLO": "PTC", "PTC": "PTC", "PUERTO ORDAZ": "PTO", "PUETO ORDAZ": "PTO", "PTO": "PTO",
        "SAN CARLOS": "SAC", "SAC": "SAC", "SAN ANTONIO DE LOS ALTOS": "SALA", "SALA": "SALA",
        "SAN FERNANDO DE APURE": "SFA", "SFA": "SFA", "SAN FELIPE": "SFL", "SFEL": "SFL", "SFL": "SFL",
        "SAN JUAN DE LOS MORROS": "SJDLM", "SJDLM": "SJDLM", "SAN CRISTOBAL": "SNCR", "SNCR": "SNCR",
        "TUCACAS": "TCCS", "TCCS": "TCCS", "EL TIGRE": "TIG", "TIG": "TIG",
        "TINAQUILLO": "TQLLO", "TQLLO": "TQLLO", "TURMERO": "TUR", "TUR": "TUR",
        "UPATA": "UPA", "UPA": "UPA", "VALENCIA": "VAL", "VAL": "VAL",
        "VALERA": "VLRA", "VLRA": "VLRA"
    }
    return mapa_ciudades.get(c, ciudad)

ciudades_validas_ve = {"ANA", "ARA", "BAR", "BQTO", "BRC", "CAR", "CAL", "CABU", "CBMA", "CBOL", "CCS", "CDOJ", "CHAR", "CMAR", "CMNA", "COR", "CUA", "CRNO", "GNRE", "GRNA", "GUAC", "GUAT", "HIG", "LEC", "LTQU", "LVIC", "MAT", "MCBO", "MER", "MRCY", "PAM", "POR", "PDM", "PTJO", "PTLC", "PTC", "PTO", "SAC", "SALA", "SFA", "SFL", "SFEL", "SJDLM", "SNCR", "TCCS", "TIG", "TQLLO", "TUR", "UPA", "VAL", "VLRA"}

def des_base64(t):
    try:
        return base64.b64decode(t).decode('utf-8', errors='ignore').replace('\x00', '').strip()
    except:
        return t

bad_chars = ["Ã", "Â", "±", "³", "¿", "¡", ",", "œ", "š", "ž", "Ÿ", "¢", "£", "¤", "¥", "¦", "§", "¨", "©", "ª", "«", "¬", "®", "¯", "°", "²", "µ", "¶", "¹", "º", "»", "¼", "½", "¾", "™"]

def tiene_caracteres_invalidos(texto):
    if pd.isna(texto): return False
    return any(char in str(texto) for char in bad_chars)

def es_correo_basura(email, id_usr):
    if pd.isna(email) or "@" not in str(email): return False
    prefijo = str(email).split("@")[0]
    
    if prefijo.isdigit(): return True
    if re.search(r'(.)\1{5,}', prefijo): return True # Letras repetidas 6 veces
    if str(id_usr) in prefijo and len(str(id_usr)) >= 6 and str(id_usr).isdigit(): return True
    
    # Sin vocales y mayor a 5 letras
    if not any(v in prefijo.lower() for v in "aeiou") and len(prefijo) >= 5: return True
    return False

# --- INTERFAZ DE STREAMLIT ---

st.set_page_config(page_title="Qualtrics DataPrep BT", layout="wide")
st.title("🧹 Limpieza de Muestra Amplitude a Qualtrics")
st.markdown("Sube tu archivo bruto de Amplitude (.csv o .xlsx) y la herramienta aplicará todas las reglas de negocio para dejarlo listo.")

archivo_subido = st.file_uploader("Carga tu base de datos aquí", type=["csv", "xlsx"])

if archivo_subido is not None:
    try:
        if archivo_subido.name.endswith('.csv'):
            df_bruto = pd.read_csv(archivo_subido, dtype=str)
        else:
            df_bruto = pd.read_excel(archivo_subido, dtype=str)
        
        st.success(f"Archivo cargado con éxito. Filas a procesar: {len(df_bruto)}")
        
        if st.button("Iniciar Limpieza", type="primary"):
            with st.spinner("Aplicando reglas de negocio (Renombrando, validando, filtrando)..."):
                
                # 1. Identificar y renombrar columnas
                col_map = {}
                for col in df_bruto.columns:
                    c_up = str(col).upper()
                    if 'IDENTIFICATION' in c_up: col_map[col] = 'External Data Reference'
                    elif 'PHONE' in c_up: col_map[col] = 'customer_phone'
                    elif 'EMAIL' in c_up: col_map[col] = 'email'
                    elif 'GENDER' in c_up: col_map[col] = 'customer_gender'
                    elif 'GP' in c_up and 'COUNTRY' in c_up: col_map[col] = 'country'
                    elif 'FIRST NAME' in c_up: col_map[col] = 'First Name'
                    elif 'LAST NAME' in c_up: col_map[col] = 'Last Name'
                    elif 'GP.CITY' in c_up or 'CITY COD' in c_up: col_map[col] = 'city'
                
                df_procesado = df_bruto[list(col_map.keys())].rename(columns=col_map).copy()
                
                # Asegurar que todas las columnas clave existan aunque vengan vacías
                columnas_requeridas = ['External Data Reference', 'customer_phone', 'email', 'customer_gender', 'country', 'First Name', 'Last Name', 'city']
                for col in columnas_requeridas:
                    if col not in df_procesado.columns:
                        df_procesado[col] = ""

                # Listas para separar resultados
                data_limpia = []
                data_eliminada = []
                contadores = {"EMAIL": 0, "PHONE": 0, "ID": 0, "CITY": 0, "PAIS_INCOHERENTE": 0}

                # 2. Procesar fila por fila
                for index, row in df_procesado.iterrows():
                    val_id = str(row['External Data Reference']).strip() if pd.notna(row['External Data Reference']) else ""
                    val_email = str(row['email']).strip().lower() if pd.notna(row['email']) else ""
                    val_phone = str(row['customer_phone']).strip() if pd.notna(row['customer_phone']) else ""
                    val_country = str(row['country']).strip().upper() if pd.notna(row['country']) else ""
                    val_city = str(row['city']).strip() if pd.notna(row['city']) else ""
                    val_fname = str(row['First Name']).strip().title() if pd.notna(row['First Name']) else ""
                    val_lname = str(row['Last Name']).strip().title() if pd.notna(row['Last Name']) else ""
                    val_gender = str(row['customer_gender']).strip().upper()[:1] if pd.notna(row['customer_gender']) else ""
                    
                    # Limpieza País
                    if val_country in ["VENEZUELA", "VE"]: val_country = "VE"
                    elif val_country in ["COLOMBIA", "CO"]: val_country = "CO"
                    
                    # Limpieza Ciudad
                    val_city = estandarizar_ciudad(val_city)
                    
                    # Limpieza Teléfono (quitar decimales si Excel los pone)
                    if val_phone.endswith('.0'): val_phone = val_phone[:-2]
                    
                    # Desencriptar ID
                    if val_id and not val_id.replace('.','').isdigit():
                        val_id = des_base64(val_id)
                    if val_id == "0.0": val_id = "0"

                    # Limpieza Género
                    if val_gender not in ["F", "M"]: val_gender = ""

                    # --- REGLAS DE DESCARTE ---
                    descartar = False
                    motivo = ""

                    if val_email == "" or "@" not in val_email or any(x in val_email for x in ["gimail", "hotmal", "yotmail", "gamail", "farmatodo", "icloud", ",", "anonimo"]) or val_email.startswith(("0414", "0424", "0412", "0416", "0426")) or tiene_caracteres_invalidos(val_email) or es_correo_basura(val_email, val_id):
                        descartar = True; motivo = "EMAIL"
                    elif val_phone == "" or "000000" in val_phone:
                        descartar = True; motivo = "PHONE"
                    elif val_id == "" or val_id == "0" or not any(char.isdigit() and char != '0' for char in val_id):
                        descartar = True; motivo = "ID"
                    elif val_city == "":
                        descartar = True; motivo = "CITY"
                    elif val_country != "VE" and val_city in ciudades_validas_ve:
                        descartar = True; motivo = "PAIS_INCOHERENTE"

                    # Armar fila procesada
                    fila_final = {
                        'External Data Reference': val_id,
                        'customer_phone': val_phone,
                        'email': val_email,
                        'customer_gender': val_gender,
                        'country': val_country,
                        'First Name': val_fname,
                        'Last Name': val_lname,
                        'city': val_city
                    }

                    if descartar:
                        fila_final['MOTIVO_ELIMINACION'] = motivo
                        data_eliminada.append(fila_final)
                        contadores[motivo] += 1
                    else:
                        data_limpia.append(fila_final)

                # 3. Crear DataFrames finales
                df_limpio = pd.DataFrame(data_limpia)
                df_eliminado = pd.DataFrame(data_eliminada)

                # 4. Mostrar Reporte
                st.divider()
                st.subheader("Reporte de Limpieza Amplitude")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Procesados", len(df_bruto))
                col2.metric("✅ Usuarios Válidos", len(df_limpio))
                col3.metric("🗑️ Total Eliminados", len(df_eliminado))

                with st.expander("Ver detalle de eliminados"):
                    st.write(f"• Por Email inválido/vacío: **{contadores['EMAIL']}**")
                    st.write(f"• Por Teléfono vacío o inválido: **{contadores['PHONE']}**")
                    st.write(f"• Por Cédula vacía: **{contadores['ID']}**")
                    st.write(f"• Por Ciudad vacía: **{contadores['CITY']}**")
                    st.write(f"• Por Incoherencia País/Ciudad: **{contadores['PAIS_INCOHERENTE']}**")

                # 5. Generar Excel descargable
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_limpio.to_excel(writer, index=False, sheet_name='BaseDatos_Limpia')
                    if not df_eliminado.empty:
                        df_eliminado.to_excel(writer, index=False, sheet_name='Usuarios Eliminados')
                
                excel_data = output.getvalue()

                st.success("¡Archivo procesado y listo para descargar!")
                st.download_button(
                    label="📥 Descargar Base Limpia para Qualtrics",
                    data=excel_data,
                    file_name="Amplitude_Limpio.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")