from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import io

# 1. Inicializamos la aplicación de FastAPI
app = FastAPI(title="Limpiador de Datos API")

# 2. Tu función original se queda EXACTAMENTE IGUAL
def estandarizar_ciudad(ciudad):
    if pd.isna(ciudad): return ""
    c = str(ciudad).strip().upper()
    c = c.replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U')
    
    mapa_ciudades = {
        "ANACO": "ANA", "ARAURE": "ARA", 
        # ... (aquí va todo tu diccionario completo) ...
    }
    return mapa_ciudades.get(c, c)
# 3. Creamos el Endpoint que recibe el archivo Excel/CSV
@app.post("/limpiar-datos/")
async def limpiar_datos(file: UploadFile = File(...)):
    
    # Leer el archivo que sube el usuario
    contents = await file.read()
    
    # Convertirlo a un DataFrame de Pandas (asumiendo que es CSV para el ejemplo)
    df = pd.read_csv(io.BytesIO(contents))
    
    # --- AQUÍ VA TU LÓGICA DE LIMPIEZA ---
    # Ejemplo: df['Ciudad_Limpia'] = df['Ciudad'].apply(estandarizar_ciudad)
    
    # Preparar el archivo limpio para devolverlo
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    # Regresar al principio del archivo virtual
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=Limpio_{file.filename}"
    
    return response